from rest_framework import serializers

from agir.checks import DonationCheckPaymentMode
from agir.groups.models import SupportGroup
from agir.lib.serializers import PhoneField
from agir.payments import payment_modes
from agir.people.models import Person

TO_LFI = "LFI"

TYPE_SINGLE_TIME = "S"
TYPE_MONTHLY = "M"

PAYMENTS_LFI_SINGLE = [payment_modes.DEFAULT_MODE, DonationCheckPaymentMode.id]
PAYMENTS_LFI_MONTHLY = [payment_modes.DEFAULT_MODE]


class DonationAllocationSerializer(serializers.Serializer):
    group = serializers.PrimaryKeyRelatedField(
        queryset=SupportGroup.objects.active().certified(),
        required=True,
    )
    amount = serializers.IntegerField(min_value=1, required=True)


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
            TO_LFI,
            "la France insoumise",
        ),
        default=TO_LFI,
    )
    amount = serializers.IntegerField(min_value=1, required=True)
    paymentTimes = serializers.ChoiceField(
        source="payment_times",
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

    # Check payment_mode is allowed for the type of donation
    def validate(self, attrs):
        payment_mode = attrs["payment_mode"]
        payment_times = attrs["payment_times"]

        error = False
        if payment_times == TYPE_MONTHLY:
            if payment_mode not in PAYMENTS_LFI_MONTHLY:
                error = True
        else:
            if payment_mode not in PAYMENTS_LFI_SINGLE:
                error = True

        if error:
            raise serializers.ValidationError(
                detail={
                    "paymentMode": f"Ce mode de paiement n'est actuellement pas autorisé pour ce type de dons"
                }
            )

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
            "paymentTimes",
            "allocations",
        )
