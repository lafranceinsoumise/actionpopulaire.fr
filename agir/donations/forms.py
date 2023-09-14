import json
import logging

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _

from agir.donations.base_forms import SimpleDonationForm
from agir.donations.form_fields import AskAmountField, AllocationsField
from agir.groups.models import SupportGroup
from agir.lib.display import display_price
from agir.payments.models import Subscription

__all__ = (
    "AllocationDonationForm",
    "AllocationDonationForm",
    "AlreadyHasSubscriptionForm",
)

logger = logging.getLogger(__name__)


class AllocationMixin(forms.Form):
    allocations = AllocationsField(
        required=False,
        queryset=SupportGroup.objects.active().certified().order_by("name").distinct(),
    )

    def __init__(self, *args, group_id=None, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.group = None

        condition = Q()

        initial_allocations = self.get_initial_for_field(
            self.fields["allocations"], "allocations"
        )
        if initial_allocations:
            condition |= Q(id__in=[g.id for g in initial_allocations])

        if group_id:
            try:
                self.group = self.fields["allocations"].queryset.get(pk=group_id)
                condition |= Q(pk=group_id)
            except (SupportGroup.DoesNotExist, ValidationError):
                pass

        if self.group:
            self.fields["allocations"].initial = {self.group: 0}

        if user.is_authenticated:
            condition |= Q(memberships__person=user.person)

        if condition:
            self.fields["allocations"].choices = self.fields[
                "allocations"
            ].queryset.filter(condition)

        self.helper.layout.fields = [
            f for f in ["type", "amount", "allocations"] if f in self.fields
        ]

    def clean(self):
        amount = self.cleaned_data.get("amount")
        allocations = self.cleaned_data.get("allocations") or {}

        if amount and sum(allocations.values()) > amount:
            self.add_error(
                "allocation",
                ValueError(
                    "Vous ne pouvez pas attribuer plus que vous n'avez donné !", "al"
                ),
            )

        if self.group is None:
            self.group = self.cleaned_data.get("group")

        return self.cleaned_data


class AllocationDonationForm(AllocationMixin, SimpleDonationForm):
    TYPE_SINGLE_TIME = "S"
    TYPE_MONTHLY = "M"

    type = forms.ChoiceField(
        label="Je souhaite donner…",
        choices=((TYPE_SINGLE_TIME, "une seule fois"), (TYPE_MONTHLY, "tous les mois")),
        help_text="En cas de don mensuel, votre carte sera débitée tous les 8 de chaque mois jusqu'à ce que vous"
        " interrompiez le don mensuel, ce que vous pouvez faire à n'importe quel moment.",
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["amount"].amount_choices = [
            200 * 100,
            100 * 100,
            50 * 100,
            10 * 100,
            5 * 100,
        ]

        self.fields["type"].widget.attrs["data-choice-attrs"] = json.dumps(
            [{"icon": "arrow-right"}, {"icon": "repeat"}]
        )


class AllocationSubscriptionForm(AllocationMixin, SimpleDonationForm):
    amount = AskAmountField(
        label="Montant du don mensuel",
        max_value=settings.MONTHLY_DONATION_MAXIMUM,
        min_value=settings.MONTHLY_DONATION_MINIMUM,
        required=True,
        error_messages={
            "invalid": _("Indiquez le montant de votre don mensuel."),
            "min_value": format_lazy(
                _("Les dons mensuels de moins de {min} ne sont pas acceptés."),
                min=display_price(settings.MONTHLY_DONATION_MINIMUM),
            ),
            "max_value": format_lazy(
                _("Les dons mensuels de plus de {max} ne sont pas acceptés."),
                max=display_price(settings.MONTHLY_DONATION_MAXIMUM),
            ),
        },
        by_month=True,
        show_tax_credit=True,
    )

    previous_subscription = forms.ModelChoiceField(
        queryset=Subscription.objects.filter(status=Subscription.STATUS_ACTIVE),
        required=False,
        widget=forms.HiddenInput,
    )

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, user=user, **kwargs)
        self.fields["amount"].amount_choices = [
            100 * 100,
            50 * 100,
            20 * 100,
            10 * 100,
            5 * 100,
        ]

        if user:
            self.fields["previous_subscription"].queryset = self.fields[
                "previous_subscription"
            ].queryset.filter(person=user.person)

        self.helper.layout.fields.append("previous_subscription")

    def get_button_label(self):
        if self.get_initial_for_field(
            self.fields["previous_subscription"], "previous_subscription"
        ):
            return "Modifier ce don mensuel"
        return "Mettre en place le don mensuel"


class AlreadyHasSubscriptionForm(forms.Form):
    choice = forms.ChoiceField(
        choices=(
            ("R", "Remplacer le paiement mensuel existant"),
            ("A", "Ajouter au paiement mensuel existant"),
        )
    )
