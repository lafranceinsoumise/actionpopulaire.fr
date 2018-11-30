import logging

from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import keep_lazy_text
from django.utils.html import mark_safe, format_html
from django.utils.formats import number_format
from django.utils.text import format_lazy

from django_countries.fields import CountryField

from crispy_forms import layout
from crispy_forms.helper import FormHelper
from webpack_loader.utils import get_files

from agir.groups.models import SupportGroup
from ..people.form_mixins import MetaFieldsMixin
from ..lib.form_components import *
from ..people.models import Person, PersonEmail


__all__ = ("DonationForm", "DonatorForm")


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

    allocation = forms.IntegerField(
        label="Montant alloué au groupe choisi",
        min_value=0,
        required=False,
        help_text="Indiquez le montant que vous souhaitez allouer à votre groupe. Le reste du don permettra de financer "
        "les actions nationales de la France insoumise.",
    )

    def __init__(self, *args, group_id=None, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.group = None

        self.helper = FormHelper()
        self.helper.form_class = "donation-form"

        if group_id:
            try:
                self.group = SupportGroup.objects.get(pk=group_id)
                self.fields["allocation"].label = format_html(
                    "{} &laquo;&nbsp;{}&nbsp;&raquo;",
                    "Montant alloué au groupe",
                    self.group.name,
                )
                self.helper.attrs["data-group-id"] = group_id
                self.helper.attrs["data-group-name"] = self.group.name
            except SupportGroup.DoesNotExist:
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

        self.helper.add_input(layout.Submit("valider", "Je donne !"))

    def clean_allocation(self):
        # return 0 when allocation is empty
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

    @property
    def media(self):
        return forms.Media(
            js=[script["url"] for script in get_files("donations/donationForm", "js")]
        )


class DonatorForm(MetaFieldsMixin, forms.ModelForm):
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
            'Un reçu, édité par la <abbr title="Commission Nationale des comptes de campagne et des financements'
            ' politiques">CNCCFP</abbr>, me sera adressé, et me permettra de déduire cette somme de mes impôts'
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

    def __init__(self, amount, allocation, group_id, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["amount"].initial = amount
        self.fields["allocation"].initial = allocation
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

        nationality, fiscal_resident = (
            cleaned_data.get("nationality"),
            cleaned_data.get("fiscal_resident"),
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
