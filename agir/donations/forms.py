import json
import logging

import reversion
from crispy_forms import layout
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Row, Submit
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
from agir.lib.form_components import *
from agir.payments.models import Subscription
from .models import SpendingRequest, Document

__all__ = (
    "AllocationDonationForm",
    "AlreadyHasSubscriptionForm",
    "SpendingRequestCreationForm",
    "SpendingRequestEditForm",
    "DocumentForm",
    "DocumentOnCreationFormset",
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


class SpendingRequestFormMixin(forms.Form):
    def __init__(self, *args, user, group, **kwargs):
        super().__init__(*args, **kwargs)

        condition = Q(organizer_configs__person=user.person) | Q(
            organizer_configs__as_group=group
        )
        self.fields["event"].queryset = (
            self.fields["event"].queryset.filter(condition).distinct().order_by("name")
        )

        self.helper = FormHelper()
        self.helper.layout = Layout(
            "title",
            "event",
            Row(
                Div("category", css_class="col-md-4"),
                Div("category_precisions", css_class="col-md-8"),
            ),
            "explanation",
            Row(
                Div("amount", css_class="col-md-4"),
                Div("spending_date", css_class="col-md-8"),
            ),
            "bank_account_name",
            "bank_account_iban",
        )


class DocumentHelper(FormHelper):
    template = "bootstrap/table_inline_formset.html"
    # Pas de tag de formulaire ni de CSRF car doit être posté
    # en même temps qu'un autre formulaire
    # le tag et le CSRF sont ajouté manuellement dans le template
    form_tag = False
    disable_csrf = True


DocumentOnCreationFormset = forms.inlineformset_factory(
    SpendingRequest, Document, fields=["title", "type", "file"], can_delete=False
)


class SpendingRequestCreationForm(SpendingRequestFormMixin, forms.ModelForm):
    def __init__(self, *args, group, **kwargs):
        super().__init__(*args, group=group, **kwargs)

        self.instance.group = group
        # Pas de tag de formulaire ni de CSRF car doit être posté
        # en même temps qu'un autre formulaire
        # le tag et le CSRF sont ajouté manuellement dans le template
        self.helper.form_tag = False
        self.helper.disable_csrf = True

    class Meta:
        model = SpendingRequest
        fields = (
            "title",
            "timing",
            "campaign",
            "event",
            "category",
            "category_precisions",
            "explanation",
            "amount",
            "spending_date",
            "bank_account_name",
            "bank_account_iban",
            "bank_account_bic",
            "bank_account_rib",
            "contact_name",
            "contact_phone",
            "contact_email",
        )


class SpendingRequestEditForm(SpendingRequestFormMixin, forms.ModelForm):
    comment = forms.CharField(
        label="Commentaire",
        widget=forms.Textarea,
        required=True,
        strip=True,
        help_text=_(
            "Merci de bien vouloir justifier les changements que vous avez apporté à votre demande."
        ),
    )

    def __init__(self, *args, instance, user, **kwargs):
        self.user = user
        super().__init__(
            *args, user=user, group=instance.group, instance=instance, **kwargs
        )

        self.helper.add_input(Submit("submit", _("Modifier")))
        self.helper.layout.fields.append("comment")

    # noinspection PyMethodOverriding
    def save(self):
        if self.has_changed():
            with reversion.create_revision():
                reversion.set_user(self.user)
                reversion.set_comment(self.cleaned_data["comment"])

                if self.instance.edition_warning:
                    self.instance.status = (
                        SpendingRequest.Status.AWAITING_SUPPLEMENTARY_INFORMATION
                    )

                return super().save()

    class Meta:
        model = SpendingRequest
        fields = (
            "title",
            "timing",
            "campaign",
            "event",
            "category",
            "category_precisions",
            "explanation",
            "amount",
            "spending_date",
            "bank_account_name",
            "bank_account_iban",
            "bank_account_bic",
            "bank_account_rib",
            "contact_name",
            "contact_phone",
            "contact_email",
        )


class DocumentForm(forms.ModelForm):
    def __init__(self, *args, user, spending_request=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if spending_request is not None:
            self.instance.request = spending_request

        self.helper = FormHelper()
        self.helper.add_input(layout.Submit("valider", "Valider"))

    # noinspection PyMethodOverriding
    def save(self):
        creating = self.instance._state.adding
        spending_request = self.instance.request

        if creating or self.has_changed():
            with reversion.create_revision():
                reversion.set_user(self.user)
                reversion.set_comment(
                    "Ajout d'un document" if creating else "Modification d'un document"
                )
                super().save()

                if spending_request.edition_warning:
                    spending_request.status = (
                        SpendingRequest.Status.AWAITING_SUPPLEMENTARY_INFORMATION
                    )
                    spending_request.save()

    class Meta:
        model = Document
        fields = ("title", "type", "file")


class AlreadyHasSubscriptionForm(forms.Form):
    choice = forms.ChoiceField(
        choices=(
            ("R", "Remplacer le paiement mensuel existant"),
            ("A", "Ajouter au paiement mensuel existant"),
        )
    )
