from crispy_forms import layout
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django import forms
from django.conf import settings
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _
from django_countries import countries
from django_countries.fields import LazyTypedChoiceField

from agir.donations.base_forms import SimpleDonationForm, BaseDonorForm
from agir.donations.form_fields import AskAmountField
from agir.lib.data import departements_choices
from agir.lib.display import display_price
from agir.lib.form_fields import IBANField
from agir.payments.payment_modes import PaymentModeField, PAYMENT_MODES
from agir.people.models import Person


class LoanForm(SimpleDonationForm):
    button_label = "Je prête !"

    amount = AskAmountField(
        label="Montant du prêt",
        max_value=settings.LOAN_MAXIMUM,
        min_value=settings.LOAN_MINIMUM,
        required=True,
        error_messages={
            "invalid": _("Indiquez le montant à prêter."),
            "min_value": format_lazy(
                _("Les prêts de moins de {min} ne sont pas acceptés."),
                min=display_price(settings.LOAN_MINIMUM),
            ),
            "max_value": format_lazy(
                _("Les prêts de plus de {max} ne peuvent être faits par carte bleue."),
                max=display_price(settings.LOAN_MAXIMUM),
            ),
        },
        amount_choices=[10000 * 100, 5000 * 100, 2000 * 100, 1000 * 100, 400 * 100],
        show_tax_credit=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = "donation-form"
        self.helper.add_input(layout.Submit("valider", self.button_label))

        self.helper.layout = Layout()


class LenderForm(BaseDonorForm):
    button_label = "Je prête {amount}"
    payment_modes = []

    country_of_birth = LazyTypedChoiceField(
        required=True,
        label="Pays de naissance",
        choices=[("", "Sélectionnez votre pays de naissance")] + list(countries),
    )
    city_of_birth = forms.CharField(label="Ville de naissance", required=True)
    departement_of_birth = forms.ChoiceField(
        label="Département de naissance (France uniquement)",
        choices=(("", "Indiquez votre département de naissance"),)
        + departements_choices,
        required=False,
    )

    amount = forms.IntegerField(
        max_value=settings.LOAN_MAXIMUM,
        min_value=settings.LOAN_MINIMUM,
        required=True,
        widget=forms.HiddenInput,
    )

    payment_mode = PaymentModeField(
        label="Comment souhaitez-vous prêter l'argent ?", payment_modes=[]
    )

    iban = IBANField(
        label="Votre IBAN",
        required=True,
        allowed_countries=["FR"],
        help_text="Le numéro IBAN du compte sur lequel le remboursement du prêt sera effectué.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["gender"].required = True
        self.fields["date_of_birth"].required = True
        self.fields["declaration"].label = _(
            "Je certifie sur l'honneur être une personne physique et que le réglement de mon prêt ne provient pas d'une"
            " personne morale mais de mon compte en banque personnel."
        )
        # retirer le help_text qui indique qu'un reçu fiscal sera émis (ce qui n'est pas le cas pour un prêt)
        self.fields["declaration"].help_text = None

        del self.fields["fiscal_resident"]

        fields = ["amount"]

        if "email" in self.fields:
            fields.append("email")

        fields.extend(
            [
                "first_name",
                "last_name",
                "gender",
                "nationality",
                layout.Field("location_address1", placeholder="Ligne 1"),
                layout.Field("location_address2", placeholder="Ligne 2"),
                layout.Row(
                    layout.Div("location_zip", css_class="col-md-4"),
                    layout.Div("location_city", css_class="col-md-8"),
                ),
                "location_country",
                "contact_phone",
                layout.Field("date_of_birth", placeholder="JJ/MM/AAAA"),
                "country_of_birth",
                "city_of_birth",
                "departement_of_birth",
                "iban",
                "payment_mode",
                "declaration",
            ]
        )

        if "subscribed_lfi" in self.fields:
            fields.append("subscribed_lfi")

        if len(self.fields["payment_mode"].payment_modes) <= 1:
            del self.fields["payment_mode"]
            fields.remove("payment_mode")

        self.helper.layout = layout.Layout(*fields)

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get("country_of_birth", "") == "FR" and not cleaned_data.get(
            "departement_of_birth", ""
        ):
            self.add_error(
                "departement_of_birth",
                forms.ValidationError(
                    "Merci d'indiquer votre département de naissance si vous êtes né⋅e en France",
                    code="departement",
                ),
            )

        if not "payment_mode" in self.fields:
            cleaned_data["payment_mode"] = PAYMENT_MODES[self.payment_modes[0]]

        return cleaned_data

    class Meta:
        model = Person
        fields = (
            "first_name",
            "last_name",
            "gender",
            "location_address1",
            "location_address2",
            "location_zip",
            "location_city",
            "location_country",
            "contact_phone",
            "date_of_birth",
        )


class ContractForm(forms.Form):
    """ """

    acceptance = forms.BooleanField(
        required=True,
        label="Je déclare solennellement avoir pris connaissance du contenu"
        " du contrat et en accepter les termes.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.add_input(layout.Submit("valider", "Je signe le contrat"))
