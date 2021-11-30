import json

from django.conf import settings
from rest_framework import serializers

from agir.donations.views import DONATION_SESSION_NAMESPACE
from agir.groups.models import SupportGroup
from agir.lib.utils import front_url_lazy
from agir.lib.serializers import PhoneField
from agir.people.models import Person
from agir.presidentielle2022 import (
    AFCP2022SystemPayPaymentMode,
    AFCPJLMCheckDonationPaymentMode,
)
from agir.payments import payment_modes
from agir.checks import DonationCheckPaymentMode

TO_LFI = "LFI"
TO_2022 = "2022"

TYPE_SINGLE_TIME = "S"
TYPE_MONTHLY = "M"

PAYMENTS_LFI_SINGLE = [payment_modes.DEFAULT_MODE, DonationCheckPaymentMode.id]
PAYMENTS_LFI_MONTHLY = [payment_modes.DEFAULT_MODE]
PAYMENTS_2022_SINGLE = [
    AFCP2022SystemPayPaymentMode.id,
    AFCPJLMCheckDonationPaymentMode.id,
]
PAYMENTS_2022_MONTHLY = [AFCP2022SystemPayPaymentMode.id]


class DonationAllocationSerializer(serializers.Serializer):
    group = serializers.PrimaryKeyRelatedField(
        queryset=SupportGroup.objects.active().certified(),
        required=True,
    )
    amount = serializers.IntegerField(min_value=1, required=True)


class CreateDonationSessionSerializer(serializers.Serializer):
    amount = serializers.IntegerField(
        min_value=settings.DONATION_MINIMUM, required=True
    )
    to = serializers.ChoiceField(
        choices=((TO_LFI, "la France insoumise"), (TO_2022, "Mélenchon 2022")),
        default=TO_LFI,
    )
    paymentTimes = serializers.ChoiceField(
        choices=((TYPE_SINGLE_TIME, "une seule fois"), (TYPE_MONTHLY, "tous les mois")),
        help_text="En cas de don mensuel, votre carte sera débitée tous les 8 de chaque mois jusqu'à ce que vous"
        " interrompiez le don mensuel, ce que vous pouvez faire à n'importe quel moment.",
        required=True,
    )
    allocations = serializers.ListField(
        child=DonationAllocationSerializer(),
        allow_empty=True,
        allow_null=True,
        required=False,
    )
    next = serializers.SerializerMethodField(read_only=True)
    allowedPaymentModes = serializers.SerializerMethodField()

    def validate(self, attrs):
        max_amount = settings.DONATION_MAXIMUM

        if attrs["paymentTimes"] == TYPE_MONTHLY:
            max_amount = settings.MONTHLY_DONATION_MAXIMUM

        if attrs["amount"] > max_amount and attrs["to"] == TO_2022:
            raise serializers.ValidationError(
                detail={
                    "amount": "Le maximum du montant total de donation pour une personne aux candidats à l'élection "
                    f"présidentielle ne peut pas excéder {int(max_amount / 100)} €"
                }
            )

        if attrs["amount"] > max_amount and attrs["to"] == TO_LFI:
            raise serializers.ValidationError(
                detail={
                    "amount": f"Les dons versés par une personne physique ne peuvent excéder {int(max_amount / 100)} €"
                }
            )

        return attrs

    def get_next(self, data):
        """
        Returns the redirection URL for the next donation step if validation succeeds
        """
        if data["to"] == TO_2022:
            return front_url_lazy("donation_2022_information_modal", absolute=True)
        return front_url_lazy("donation_information_modal", absolute=True)

    def get_allowedPaymentModes(self, data):
        """
        Returns the payment modes allowed switch type given 2022 | LFI | MONTHLY | ..
        """

        if data["to"] == TO_2022:
            if data["paymentTimes"] == TYPE_MONTHLY:
                return PAYMENTS_2022_MONTHLY
            return PAYMENTS_2022_SINGLE

        if data["paymentTimes"] == TYPE_MONTHLY:
            return PAYMENTS_LFI_MONTHLY
        if data["paymentTimes"] == TYPE_SINGLE_TIME:
            return PAYMENTS_LFI_SINGLE

        return [payment_modes.DEFAULT_MODE]

    def create(self, validated_data):
        session = self.context["request"].session
        session[DONATION_SESSION_NAMESPACE] = {**validated_data}
        if "allocations" in validated_data:
            session[DONATION_SESSION_NAMESPACE]["allocations"] = json.dumps(
                [
                    {**allocation, "group": str(allocation["group"].id)}
                    for allocation in validated_data.get("allocations", [])
                ]
            )

        # Add payment_modes in session
        session[DONATION_SESSION_NAMESPACE][
            "allowedPaymentModes"
        ] = self.get_allowedPaymentModes(validated_data)
        return validated_data


class SendDonationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)
    firstName = serializers.CharField(max_length=255, source="first_name")
    lastName = serializers.CharField(max_length=255, source="last_name")
    locationAddress1 = serializers.CharField(max_length=100, source="location_address1")
    locationAddress2 = serializers.CharField(
        max_length=100, source="location_address2", required=False, allow_blank=True
    )
    locationCity = serializers.CharField(max_length=100, source="location_city")
    locationZip = serializers.CharField(max_length=20, source="location_zip")
    locationCountry = serializers.CharField(max_length=100, source="location_country")
    contactPhone = PhoneField(max_length=30, required=True, source="contact_phone")
    nationality = serializers.CharField(max_length=100)

    subscribed2022 = serializers.BooleanField(required=False, source="subscribed_2022")
    is2022 = serializers.BooleanField(required=False, source="is_2022")

    paymentMode = serializers.CharField(max_length=20, source="payment_mode")
    to = serializers.ChoiceField(
        choices=((TO_LFI, "la France insoumise"), (TO_2022, "Mélenchon 2022")),
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
        to = attrs["to"]
        payment_times = attrs["payment_times"]

        error = False
        if to == TO_2022:
            if payment_times == TYPE_MONTHLY:
                if payment_mode not in PAYMENTS_2022_MONTHLY:
                    error = True
            else:
                if payment_mode not in PAYMENTS_2022_SINGLE:
                    error = True
        # LFI
        else:
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

        # Update newsletters and support only if checked
        if "subscribed_2022" in validated_data and validated_data["subscribed_2022"]:
            if Person.NEWSLETTER_2022 not in self.instance.newsletters:
                self.instance.newsletters.append(Person.NEWSLETTER_2022)
            if Person.NEWSLETTER_2022_EXCEPTIONNEL not in self.instance.newsletters:
                self.instance.newsletters.append(Person.NEWSLETTER_2022_EXCEPTIONNEL)

        if "is_2022" in validated_data and not validated_data["is_2022"]:
            del validated_data["is_2022"]

        if self.instance is not None and "email" in validated_data:
            del validated_data["email"]

        super().save(**validated_data)

    class Meta:
        model = Person
        fields = (
            "email",
            "firstName",
            "lastName",
            "locationAddress1",
            "locationAddress2",
            "locationCity",
            "locationZip",
            "locationCountry",
            "contactPhone",
            "nationality",
            "subscribed2022",
            "is2022",
            "paymentMode",
            "to",
            "amount",
            "paymentTimes",
            "allocations",
        )
