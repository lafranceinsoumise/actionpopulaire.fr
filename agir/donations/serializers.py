from rest_framework import serializers

from agir.checks import DonationCheckPaymentMode
from agir.donations.models import AllocationModelMixin
from agir.groups.models import SupportGroup
from agir.lib.data import departements_choices
from agir.lib.serializers import PhoneField
from agir.payments import payment_modes
from agir.people.models import Person

TO_LFI_DONATIONS = "DONATION"
TO_LFI_CONTRIBUTIONS = "CONTRIBUTION"

TYPE_SINGLE_TIME = "S"
TYPE_MONTHLY = "M"

PAYMENTS_LFI_SINGLE = [payment_modes.DEFAULT_MODE, DonationCheckPaymentMode.id]
PAYMENTS_LFI_MONTHLY = [payment_modes.DEFAULT_MODE]


class DonationAllocationSerializer(serializers.Serializer):
    type = serializers.ChoiceField(
        choices=AllocationModelMixin.TYPE_CHOICES,
        default=AllocationModelMixin.TYPE_GROUP,
        required=False,
    )
    group = serializers.PrimaryKeyRelatedField(
        queryset=SupportGroup.objects.active().certified(), required=False
    )
    departement = serializers.ChoiceField(choices=departements_choices, required=False)
    amount = serializers.IntegerField(min_value=1, required=True)

    def validate(self, attrs):
        if attrs.get("group"):
            attrs["group"] = str(attrs["group"].id)

        if attrs.get("type") == AllocationModelMixin.TYPE_GROUP and not attrs.get(
            "group"
        ):
            raise serializers.ValidationError(
                detail={
                    "group": "L'id du groupe est obligatoire pour ce type d'allocation"
                }
            )

        if attrs.get("type") == AllocationModelMixin.TYPE_DEPARTEMENT and not attrs.get(
            "departement"
        ):
            raise serializers.ValidationError(
                detail={
                    "departement": "Le code du departement est obligatoire pour ce type d'allocation"
                }
            )

        return attrs


class DonationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)
    firstName = serializers.CharField(max_length=255, source="first_name")
    lastName = serializers.CharField(max_length=255, source="last_name")
    gender = serializers.CharField()
    locationAddress1 = serializers.CharField(max_length=100, source="location_address1")
    locationAddress2 = serializers.CharField(
        max_length=100, source="location_address2", required=False, allow_blank=True
    )
    locationCity = serializers.CharField(max_length=100, source="location_city")
    locationZip = serializers.CharField(max_length=20, source="location_zip")
    locationCountry = serializers.CharField(max_length=100, source="location_country")
    contactPhone = PhoneField(max_length=30, required=True, source="contact_phone")
    nationality = serializers.CharField(max_length=100)

    paymentMode = serializers.CharField(max_length=20, source="payment_mode")
    to = serializers.ChoiceField(
        choices=(
            (TO_LFI_DONATIONS, "don à la France insoumise"),
            (TO_LFI_CONTRIBUTIONS, "contribution à la France insoumise"),
        ),
        default=TO_LFI_DONATIONS,
    )
    amount = serializers.IntegerField(min_value=1, required=True)
    paymentTiming = serializers.ChoiceField(
        source="payment_timing",
        choices=((TYPE_SINGLE_TIME, "une seule fois"), (TYPE_MONTHLY, "tous les mois")),
        required=True,
    )
    allocations = serializers.ListField(
        child=DonationAllocationSerializer(),
        allow_empty=True,
        allow_null=True,
        required=False,
    )

    def validate_email(self, value):
        if self.instance is None and value is None:
            raise serializers.ValidationError("L'email est obligatoire.")
        return value

    def validate_lfi_donations(self, attrs):
        payment_mode = attrs["payment_mode"]
        error = False

        if attrs["payment_timing"] == TYPE_MONTHLY:
            if payment_mode not in PAYMENTS_LFI_MONTHLY:
                error = True
        elif attrs["payment_timing"] == TYPE_SINGLE_TIME:
            if payment_mode not in PAYMENTS_LFI_SINGLE:
                error = True

        if error:
            raise serializers.ValidationError(
                detail={
                    "paymentMode": "Ce mode de paiement n'est actuellement pas autorisé pour ce type de dons"
                }
            )
        return attrs

    def validate_lfi_contributions(self, attrs):
        payment_mode = attrs.get("payment_mode")
        # TODO: set payment end date based on current month (?)
        # TODO: validate unique contribution for email

        if payment_mode not in PAYMENTS_LFI_MONTHLY:
            # Force single time payment for checks
            attrs["payment_timing"] = TYPE_SINGLE_TIME
            # TODO: update amount and allocations to pay all at once
        else:
            # Force monthly payment for system pay
            attrs["payment_timing"] = TYPE_MONTHLY

        return attrs

    def validate_allocation_amount(self, attrs):
        allocations = attrs.get("allocations")
        if allocations:
            amount = attrs.get("amount")
            total_allocations = sum(
                [allocation.get("amount", 0) for allocation in allocations]
            )
            if total_allocations > amount:
                raise serializers.ValidationError(
                    detail={
                        "allocations": "La somme des montants des allocations est supérieur au montant total"
                    }
                )

        return attrs

    def validate(self, attrs):
        to = attrs.get("to")

        if to == TO_LFI_CONTRIBUTIONS:
            attrs = self.validate_lfi_contributions(attrs)
        elif to == TO_LFI_DONATIONS:
            attrs = self.validate_lfi_donations(attrs)

        attrs = self.validate_allocation_amount(attrs)

        return attrs

    def save(self, **kwargs):
        validated_data = self.validated_data

        if self.instance is not None and "email" in validated_data:
            del validated_data["email"]

        super().save(**validated_data)

    class Meta:
        model = Person
        fields = (
            "email",
            "firstName",
            "lastName",
            "gender",
            "locationAddress1",
            "locationAddress2",
            "locationCity",
            "locationZip",
            "locationCountry",
            "contactPhone",
            "nationality",
            "paymentMode",
            "to",
            "amount",
            "paymentTiming",
            "allocations",
        )
