from data_france.models import Commune, CirconscriptionConsulaire
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from agir.people.serializers import PersonNewsletterListField
from agir.voting_proxies.actions import (
    create_or_update_voting_proxy,
    create_or_update_voting_proxy_request,
    update_voting_proxy,
)
from agir.voting_proxies.models import VotingProxyRequest, VotingProxy


class CommuneOrConsulateSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    type = serializers.SerializerMethodField()
    value = serializers.IntegerField(read_only=True, source="id")
    label = serializers.SerializerMethodField(read_only=True)

    def get_label(self, instance):
        if isinstance(instance, Commune):
            return f"{instance.code_departement} - {instance.nom}"
        if isinstance(instance, CirconscriptionConsulaire):
            return str(instance)

    def get_type(self, instance):
        if isinstance(instance, Commune):
            return "commune"
        if isinstance(instance, CirconscriptionConsulaire):
            return "consulate"


class VoterSerializerMixin(serializers.ModelSerializer):
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
        required=False,
        allow_blank=True,
        default="",
        source="polling_station_number",
        label="Numéro du bureau de vote",
    )
    updated = serializers.BooleanField(
        default=False,
        read_only=True,
    )

    def validate_required_commune_or_consulate(self, attrs):
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


class VotingProxyRequestSerializer(VoterSerializerMixin):
    votingDates = serializers.MultipleChoiceField(
        required=True,
        allow_empty=False,
        choices=VotingProxyRequest.VOTING_DATE_CHOICES,
        label="Scrutins",
    )

    def validate(self, attrs):
        attrs = super().validate(attrs)

        self.validate_required_commune_or_consulate(attrs)

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
        return create_or_update_voting_proxy_request(validated_data)

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


class VotingProxySerializer(VoterSerializerMixin):
    email = serializers.ReadOnlyField()
    votingDates = serializers.MultipleChoiceField(
        source="voting_dates",
        required=True,
        allow_empty=False,
        choices=[(str(date), label) for date, label in VotingProxy.VOTING_DATE_CHOICES],
        label="Scrutins",
    )
    dateOfBirth = serializers.DateField(source="date_of_birth", required=True)

    def update(self, instance, validated_data):
        if "commune" in validated_data or "consulate" in validated_data:
            validated_data["commune"] = validated_data.get("commune", instance.commune)
            validated_data["consulate"] = validated_data.get(
                "consulate", instance.consulate
            )
            self.validate_required_commune_or_consulate(validated_data)

        return update_voting_proxy(instance, validated_data)

    class Meta:
        model = VotingProxy
        fields = (
            "firstName",
            "lastName",
            "email",
            "phone",
            "commune",
            "consulate",
            "pollingStationNumber",
            "votingDates",
            "remarks",
            "status",
            "dateOfBirth",
        )


class CreateVotingProxySerializer(VotingProxySerializer):
    email = serializers.EmailField(required=True)
    person = serializers.UUIDField(read_only=True, source="person_id")
    newsletters = PersonNewsletterListField(
        required=False, allow_empty=True, write_only=True
    )
    address = serializers.CharField(write_only=True, required=False, allow_blank=True)
    zip = serializers.CharField(write_only=True, required=False, allow_blank=True)
    city = serializers.CharField(write_only=True, required=False, allow_blank=True)

    def validate_required_address_for_commune(self, attrs):
        if attrs.get("commune", None) is None:
            return attrs
        errors = {}
        if not attrs.get("address", None):
            errors["address"] = "Veuillez indiquer une adresse"
        if not attrs.get("zip", None):
            errors["zip"] = "Veuillez indiquer un code postal"
        if not attrs.get("city", None):
            errors["city"] = "Veuillez indiquer une ville"
        if len(errors.keys()) > 0:
            raise ValidationError(errors)

        return attrs

    def validate(self, attrs):
        super().validate(attrs)
        self.validate_required_commune_or_consulate(attrs)
        self.validate_required_address_for_commune(attrs)

        return attrs

    def create(self, validated_data):
        return create_or_update_voting_proxy(validated_data)

    class Meta:
        model = VotingProxy
        fields = (
            "firstName",
            "lastName",
            "email",
            "phone",
            "commune",
            "consulate",
            "pollingStationNumber",
            "votingDates",
            "remarks",
            "person",
            "newsletters",
            "updated",
            "dateOfBirth",
            "address",
            "zip",
            "city",
        )
