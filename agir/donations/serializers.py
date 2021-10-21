import json

from rest_framework import serializers

from agir.donations.views import DONATION_SESSION_NAMESPACE
from agir.groups.models import SupportGroup
from agir.lib.utils import front_url_lazy
from agir.lib.serializers import PhoneField
from agir.payments.payment_modes import PAYMENT_MODES
from agir.donations import AFCP2022SystemPayPaymentMode
from agir.checks import AFCPJLMCheckPaymentMode
from agir.payments import payment_modes

MAX_AMOUNT_LFI = 750000
MAX_AMOUNT_2022 = 460000

TO_LFI = "LFI"
TO_2022 = "2022"

TYPE_SINGLE_TIME = "S"
TYPE_MONTHLY = "M"


class DonationAllocationSerializer(serializers.Serializer):
    group = serializers.PrimaryKeyRelatedField(
        queryset=SupportGroup.objects.active().certified(), required=True,
    )
    amount = serializers.IntegerField(min_value=1, required=True)


class CreateDonationSerializer(serializers.Serializer):
    amount = serializers.IntegerField(min_value=1, required=True)
    to = serializers.ChoiceField(
        choices=((TO_LFI, "la France insoumise"), (TO_2022, "Mélenchon 2022")),
        default=TO_LFI,
    )
    type = serializers.ChoiceField(
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
    allowedPaymentModes = serializers.SerializerMethodField(read_only=True)

    def validate(self, attrs):
        if attrs["to"] == TO_2022 and attrs["amount"] > MAX_AMOUNT_2022:
            raise serializers.ValidationError(
                detail={
                    "amount": f"Les dons versés par une personne physique ne peuvent excéder {int(MAX_AMOUNT_LFI / 100)} € par an pour un  ou des partis ou groupements politiques "
                }
            )

        if attrs["to"] == TO_LFI and attrs["amount"] > MAX_AMOUNT_LFI:
            raise serializers.ValidationError(
                detail={
                    "amount": f"Le maximum du montant total de donation pour une personne aux candidats à l'élection présidentielle ne peut pas excéder {int(MAX_AMOUNT_2022 / 100)} €"
                }
            )

        return attrs

    def get_next(self, data):
        """
        Returns the redirection URL for the next donation step if validation succeeds
        """
        if data["to"] == TO_2022 and data["type"] == TYPE_MONTHLY:
            return front_url_lazy("monthly_donation_2022_information", absolute=True)
        if data["to"] == TO_2022:
            return front_url_lazy("donation_2022_information", absolute=True)
        if data["type"] == TYPE_MONTHLY:
            return front_url_lazy("monthly_donation_information", absolute=True)
        if data["type"] == TYPE_SINGLE_TIME:
            return front_url_lazy("donation_information", absolute=True)

    def get_allowedPaymentModes(self, data):
        """
        Returns the payment modes allowed switch type given 2022 | LFI | MONTHLY | ..
        """

        # Forbid monthly payment for 2022 for now
        # if data["to"] == TO_2022 and data["type"] == TYPE_MONTHLY:
        #     return AFCP2022SystemPayPaymentMode.id

        if data["to"] == TO_2022:
            return [AFCP2022SystemPayPaymentMode, AFCPJLMCheckPaymentMode]
        if data["type"] == TYPE_MONTHLY:
            return [payment_modes.DEFAULT_MODE]
        if data["type"] == TYPE_SINGLE_TIME:
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
        # session[DONATION_SESSION_NAMESPACE]["allowedPaymentModes"] = self.get_allowedPaymentModes(validated_data)
        return validated_data


class SendDonationSerializer(serializers.Serializer):

    email = serializers.EmailField()
    firstName = serializers.CharField(max_length=255, source="first_name")
    lastName = serializers.CharField(max_length=255, source="last_name")
    locationAddress1 = serializers.CharField(max_length=100, source="location_address1")
    locationCity = serializers.CharField(max_length=100, source="location_city")
    locationZip = serializers.CharField(max_length=20, source="location_zip")
    locationCountry = serializers.CharField(max_length=100, source="location_country")

    contactPhone = PhoneField(max_length=30, required=True, source="contact_phone")
    nationality = serializers.CharField(max_length=100)

    subscribedLfi = serializers.BooleanField(required=False, source="subscribed_lfi")

    paymentMode = serializers.CharField(max_length=20, source="payment_mode")

    to = serializers.ChoiceField(
        choices=((TO_LFI, "la France insoumise"), (TO_2022, "Mélenchon 2022")),
        default=TO_LFI,
    )
    amount = serializers.IntegerField(min_value=1, required=True)
    type = serializers.ChoiceField(
        choices=((TYPE_SINGLE_TIME, "une seule fois"), (TYPE_MONTHLY, "tous les mois")),
        required=True,
    )
    allocations = serializers.ListField(
        child=DonationAllocationSerializer(),
        allow_empty=True,
        allow_null=True,
        required=False,
    )
