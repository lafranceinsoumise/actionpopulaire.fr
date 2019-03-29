import logging

import reversion
from crispy_forms import layout
from crispy_forms.helper import FormHelper
from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from agir.donations.base_forms import SimpleDonationForm, SimpleDonorForm
from agir.groups.models import SupportGroup
from agir.lib.data import FRANCE_COUNTRY_CODES
from agir.lib.form_components import *
from .models import SpendingRequest, Document

__all__ = ("AllocationDonationForm", "AllocationDonorForm")


logger = logging.getLogger(__name__)


class AllocationDonationForm(SimpleDonationForm):
    group = forms.ModelChoiceField(
        label="Groupe à financer",
        queryset=SupportGroup.objects.active().certified().order_by("name"),
        empty_label="Aucun groupe",
        required=False,
        help_text="Vous pouvez désigner un groupe auquel votre don sera en partie ou en totalité alloué. Si vous "
        "voulez choisir un groupe dont vous n'être pas membre, rendez-vous sur la page de ce groupe et "
        "cliquez sur &laquo;&nbsp;Financer les actions de ce groupe&nbsp;&raquo;",
    )

    allocation = forms.DecimalField(
        label="Montant alloué au groupe choisi",
        decimal_places=2,
        min_value=0,
        required=False,
        help_text="Indiquez le montant que vous souhaitez allouer à votre groupe. Le reste du don permettra de financer "
        "les actions nationales de la France insoumise.",
    )

    def __init__(self, *args, group_id=None, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.group = None

        if group_id:
            try:
                self.group = self.fields["group"].queryset.get(pk=group_id)
                self.fields["allocation"].label = format_html(
                    "{} &laquo;&nbsp;{}&nbsp;&raquo;",
                    "Montant alloué au groupe",
                    self.group.name,
                )
                self.helper.attrs["data-group-id"] = group_id
                self.helper.attrs["data-group-name"] = self.group.name
            except (SupportGroup.DoesNotExist, ValidationError):
                pass

        if self.group is None and user.is_authenticated:
            self.fields["group"].queryset = self.fields["group"].queryset.filter(
                memberships__person=user.person
            )

        if self.group is not None:
            del self.fields["group"]
        elif user.is_anonymous or not self.fields["group"].queryset:
            del self.fields["group"]
            del self.fields["allocation"]

    def clean_allocation(self):
        return self.cleaned_data.get("allocation") or 0

    def clean(self):
        amount = self.cleaned_data.get("amount")
        allocation = self.cleaned_data.get("allocation", 0)

        if amount and allocation > amount:
            self.add_error(
                "allocation",
                ValueError(
                    "Vous ne pouvez pas attribuer plus que vous n'avez donné !", "al"
                ),
            )

        if self.group is None:
            self.group = self.cleaned_data.get("group")

        return self.cleaned_data


class AllocationDonorForm(SimpleDonorForm):
    allocation = forms.IntegerField(
        min_value=0, required=True, widget=forms.HiddenInput
    )

    group = forms.ModelChoiceField(
        queryset=SupportGroup.objects.active(), required=False, widget=forms.HiddenInput
    )

    def __init__(self, *args, allocation, group_id, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["allocation"].initial = allocation
        self.fields["group"].initial = group_id

    def clean(self):
        cleaned_data = super().clean()

        nationality, fiscal_resident, location_country = (
            cleaned_data.get("nationality"),
            cleaned_data.get("fiscal_resident"),
            cleaned_data.get("location_country"),
        )

        if nationality != "FR" and not fiscal_resident:
            self.add_error(
                "fiscal_resident",
                forms.ValidationError(
                    _(
                        "Les personnes non-françaises doivent être fiscalement domiciliées en France."
                    ),
                    code="not_fiscal_resident",
                ),
            )

        if fiscal_resident and location_country not in FRANCE_COUNTRY_CODES:
            self.add_error(
                "location_country",
                forms.ValidationError(
                    _(
                        "Pour pouvoir donner si vous n'êtes pas français, vous devez être domicilié⋅e fiscalement en"
                        " France et nous indiquer votre adresse fiscale en France."
                    )
                ),
            )

        amount = self.cleaned_data.get("amount")
        allocation = self.cleaned_data.get("allocation", 0)

        if amount and allocation > amount:
            self.add_error(
                None,
                ValueError(
                    "Il y a une erreur inattendue sur le formulaire. Réessayez la procédure depuis le tout début",
                    "allocation",
                ),
            )

        return cleaned_data


class SpendingRequestFormMixin:
    def __init__(self, *args, user, group, **kwargs):
        super().__init__(*args, **kwargs)

        condition = Q(organizer_configs__person=user.person) | Q(
            organizer_configs__as_group=group
        )
        self.fields["event"].queryset = (
            self.fields["event"].queryset.filter(condition).distinct().order_by("name")
        )


class DocumentHelper(FormHelper):
    template = "bootstrap/table_inline_formset.html"
    form_tag = False
    disable_csrf = True


DocumentOnCreationFormset = forms.inlineformset_factory(
    SpendingRequest, Document, fields=["title", "type", "file"], can_delete=False
)


class SpendingRequestCreationForm(SpendingRequestFormMixin, forms.ModelForm):
    def __init__(self, *args, group, **kwargs):
        super().__init__(*args, group=group, **kwargs)

        self.instance.group = group
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True

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
            "provider",
            "iban",
        )

    class Meta:
        model = SpendingRequest
        fields = (
            "title",
            "event",
            "category",
            "category_precisions",
            "explanation",
            "amount",
            "spending_date",
            "provider",
            "iban",
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

        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", _("Modifier")))

    # noinspection PyMethodOverriding
    def save(self):
        if self.has_changed():
            with reversion.create_revision():
                reversion.set_user(self.user)
                reversion.set_comment(self.cleaned_data["comment"])

                if self.instance.status in SpendingRequest.STATUS_EDITION_MESSAGES:
                    self.instance.status = (
                        SpendingRequest.STATUS_AWAITING_SUPPLEMENTARY_INFORMATION
                    )

                return super().save()

    class Meta:
        model = SpendingRequest
        fields = (
            "title",
            "event",
            "category",
            "category_precisions",
            "explanation",
            "amount",
            "spending_date",
            "provider",
            "iban",
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

                if spending_request.status in SpendingRequest.STATUS_EDITION_MESSAGES:
                    spending_request.status = (
                        SpendingRequest.STATUS_AWAITING_SUPPLEMENTARY_INFORMATION
                    )
                    spending_request.save()

    class Meta:
        model = Document
        fields = ("title", "type", "file")
