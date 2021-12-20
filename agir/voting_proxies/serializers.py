from copy import deepcopy

from data_france.models import Commune, CirconscriptionConsulaire
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from agir.voting_proxies.models import VotingProxyRequest


class CommuneOrConsulateSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True, source="__str__")
    type = serializers.SerializerMethodField()

    def get_type(self, instance):
        if isinstance(instance, Commune):
            return "commune"
        if isinstance(instance, CirconscriptionConsulaire):
            return "consulate"


class VotingProxyRequestSerializer(serializers.ModelSerializer):
    firstName = serializers.CharField(
        required=True, source="first_name", label="Prénom"
    )
    lastName = serializers.CharField(required=True, source="last_name", label="Nom")
    email = serializers.EmailField(required=True, label="Adresse e-mail")
    phone = PhoneNumberField(
        required=True, source="contact_phone", label="Numéro de téléphone"
    )
    commune = serializers.PrimaryKeyRelatedField(
        required=False,
        allow_null=True,
        label="Commune",
        queryset=Commune.objects.filter(
            type__in=(Commune.TYPE_COMMUNE, Commune.TYPE_ARRONDISSEMENT_PLM),
        ).exclude(code__in=("75056", "69123", "13055")),
    )
    consulate = serializers.PrimaryKeyRelatedField(
        required=False,
        allow_null=True,
        label="Circonscription consulaire",
        queryset=CirconscriptionConsulaire.objects.all(),
    )
    pollingStationNumber = serializers.CharField(
        required=True, source="polling_station_number", label="Numéro du bureau de vote"
    )
    votingDates = serializers.MultipleChoiceField(
        required=True,
        allow_empty=False,
        choices=(VotingProxyRequest.VOTING_DATE_CHOICES),
        label="Scrutins",
    )
    updated = serializers.BooleanField(
        default=False,
        read_only=True,
    )

    def validate(self, attrs):
        attrs = super().validate(attrs)

        commune = attrs.get("commune", None)
        consulate = attrs.get("consulate", None)

        if commune is None and consulate is None:
            raise ValidationError(
                {
                    "commune": "Au moins une commune ou une circonscription consulaire doit être sélectionnée",
                    "consulate": "Au moins une commune ou une circonscription consulaire doit être sélectionnée",
                },
                code="invalid_missing_commune_and_consulate",
            )

        if commune is not None and consulate is not None:
            raise ValidationError(
                {
                    "commune": "Une commune et une circonscription consulaire ne peuvent pas être sélectionnées en "
                    "même temps",
                    "consulate": "Une commune et une circonscription consulaire ne peuvent pas être sélectionnées en "
                    "même temps",
                },
                code="invalid_commune_and_consulate",
            )

        # Prevent updates for requests that have a non-null `proxy` field
        if VotingProxyRequest.objects.filter(
            voting_date__in=attrs.get("votingDates"),
            email=attrs.get("email"),
            proxy__isnull=False,
        ).exists():
            raise ValidationError(
                {
                    "global": "Une demande de vote par procuration existe déjà pour certaines "
                    "des dates sélectionnées et pour cette adresse e-mail "
                },
                code="invalid_already_exists",
            )

        return attrs

    def create(self, validated_data):
        data = deepcopy(validated_data)
        email = data.pop("email")

        for voting_date in data.pop("votingDates"):
            (request, created) = VotingProxyRequest.objects.update_or_create(
                voting_date=voting_date,
                email=email,
                defaults={**data},
            )
            if not created:
                validated_data["updated"] = True

        return validated_data

    class Meta:
        model = VotingProxyRequest
        fields = (
            "firstName",
            "lastName",
            "email",
            "phone",
            "commune",
            "consulate",
            "pollingStationNumber",
            "votingDates",
            "updated",
        )
