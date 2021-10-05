import json

from rest_framework import serializers

from agir.donations.views import DONATION_SESSION_NAMESPACE
from agir.groups.models import SupportGroup
from agir.lib.utils import front_url_lazy

TO_LFI = "LFI"
TO_JLM2022 = "2022"

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
        choices=((TO_LFI, "la France insoumise"), (TO_JLM2022, "Mélenchon 2022")),
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

    def get_next(self, data):
        """
        Returns the redirection URL for the next donation step if validation succeeds
        """
        if data and data["to"] == TO_JLM2022:
            return front_url_lazy("donation_2022_information", absolute=True)
        if data and data["type"] == TYPE_MONTHLY:
            return front_url_lazy("monthly_donation_information", absolute=True)
        if data and data["type"] == TYPE_SINGLE_TIME:
            return front_url_lazy("donation_information", absolute=True)

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
        return validated_data
