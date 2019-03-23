import logging

import reversion
from crispy_forms import layout
from crispy_forms.helper import FormHelper
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.formats import number_format
from django.utils.functional import keep_lazy_text
from django.utils.html import mark_safe, format_html
from django.utils.text import format_lazy
from django.utils.translation import ugettext_lazy as _
from django_countries.fields import CountryField

from agir.groups.models import SupportGroup
from agir.lib.data import FRANCE_COUNTRY_CODES
from agir.lib.form_components import *
from agir.lib.form_mixins import MetaFieldsMixin
from agir.people.models import Person, PersonEmail
from .models import SpendingRequest, Document

__all__ = ("DonationForm", "DonorForm")


logger = logging.getLogger(__name__)


class DonationForm(forms.Form):
    amount = forms.DecimalField(
        label="Montant du don",
        max_value=settings.DONATION_MAXIMUM,
        min_value=settings.DONATION_MINIMUM,
        decimal_places=2,
        required=True,
        error_messages={
            "invalid": _("Indiquez le montant à donner."),
            "min_value": format_lazy(
                _("Il n'est pas possible de donner moins que {min} €."),
                min=settings.DONATION_MINIMUM,
            ),
            "max_value": format_lazy(
                _("Les dons de plus de {max} € ne peuvent être faits par carte bleue."),
                max=settings.DONATION_MAXIMUM,
            ),
        },
    )

    group = forms.ModelChoiceField(
        label="Groupe à financer",
        queryset=SupportGroup.objects.active().certified().order_by("name"),
        empty_label="Aucun groupe",
        required=False,
        help_text="Vous pouvez désigner un groupe auquel votre don sera en partie ou en totalité alloué.",
    )

    allocation = forms.DecimalField(
        label="Montant alloué au groupe choisi",
        decimal_places=2,
        min_value=0,
        required=False,
        help_text="Indiquez le montant que vous souhaitez allouer à votre groupe. Le reste du don permettra de financer "
        "les actions nationales de la France insoumise.",
    )

    def __init__(self, *args, enable_allocations, group_id=None, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.group = None

        self.helper = FormHelper()
        self.helper.form_class = "donation-form"

        if enable_allocations:
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
        else:
            del self.fields["group"]
            del self.fields["allocation"]

        self.helper.add_input(layout.Submit("valider", "Je donne !"))

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


class DonorForm(MetaFieldsMixin, forms.ModelForm):
    meta_fields = ["nationality"]

    email = forms.EmailField(
        label=_("Votre adresse email"),
        required=True,
        help_text=_(
            "Si vous êtes déjà inscrit⋅e sur la plateforme, utilisez l'adresse avec laquelle vous êtes inscrit⋅e"
        ),
    )

    amount = forms.IntegerField(
        max_value=settings.DONATION_MAXIMUM * 100,
        min_value=settings.DONATION_MINIMUM * 100,
        required=True,
        widget=forms.HiddenInput,
    )

    allocation = forms.IntegerField(
        min_value=0, required=True, widget=forms.HiddenInput
    )

    group = forms.ModelChoiceField(
        queryset=SupportGroup.objects.active(), required=False, widget=forms.HiddenInput
    )

    declaration = forms.BooleanField(
        required=True,
        label=_(
            "Je certifie sur l'honneur être une personne physique et que le réglement de mon don ne provient pas"
            " d'une personne morale (association, société, société civile...) mais de mon compte bancaire"
            " personnel."
        ),
        help_text=keep_lazy_text(mark_safe)(
            "Un reçu détaché d'une formule numérotée éditée par la Commission nationale des comptes de campagne"
            " me sera adressé, et me permettra de déduire cette somme de mes impôts"
            " dans les limites fixées par la loi."
        ),
    )

    nationality = CountryField(
        blank=False, blank_label=_("Indiquez le pays dont vous êtes citoyen")
    ).formfield(
        label=_("Nationalité"),
        help_text=_(
            "Indiquez France, si vous êtes de double nationalité, dont française."
        ),
    )

    fiscal_resident = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={"disabled": True}),
        label=_("Je certifie être domicilié⋅e fiscalement en France"),
    )

    def __init__(
        self, enable_allocations, amount, allocation, group_id, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.fields["amount"].initial = amount

        if enable_allocations:
            self.fields["allocation"].initial = allocation
        else:
            del self.fields["allocation"]

        self.fields["group"].initial = group_id

        self.adding = self.instance._state.adding

        if not self.adding:
            del self.fields["email"]

        # we remove the subscribed field for people who are already subscribed
        if not self.adding and self.instance.subscribed:
            del self.fields["subscribed"]
        else:
            # we want the subscribed field to be prechecked only for new email subscribers
            self.fields["subscribed"].initial = self.adding

        for f in [
            "first_name",
            "last_name",
            "location_address1",
            "location_zip",
            "location_city",
            "location_country",
            "contact_phone",
        ]:
            self.fields[f].required = True
        self.fields["location_address1"].label = "Adresse"
        self.fields["location_address2"].label = False

        fields = ["amount", "group", "allocation"]

        if "email" in self.fields:
            fields.append("email")

        fields.extend(["declaration", "nationality", "fiscal_resident"])
        fields.extend(["first_name", "last_name"])
        fields.extend(
            [
                layout.Field("location_address1", placeholder="Ligne 1"),
                layout.Field("location_address2", placeholder="Ligne 2"),
            ]
        )

        fields.append(
            Row(
                layout.Div("location_zip", css_class="col-md-4"),
                layout.Div("location_city", css_class="col-md-8"),
            )
        )

        fields.append("location_country")

        fields.append("contact_phone")

        self.helper = FormHelper()
        self.helper.add_input(
            layout.Submit("valider", f"Je donne {number_format(amount / 100, 2)} €")
        )
        self.helper.layout = layout.Layout(*fields)

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

    def _save_m2m(self):
        if self.adding:
            PersonEmail.objects.create_email(
                address=self.cleaned_data["email"], person=self.instance
            )

    class Meta:
        model = Person
        fields = (
            "first_name",
            "last_name",
            "location_address1",
            "location_address2",
            "location_zip",
            "location_city",
            "location_country",
            "contact_phone",
            "subscribed",
        )


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
