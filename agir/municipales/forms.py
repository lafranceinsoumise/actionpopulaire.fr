from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset
from django import forms
from django.conf import settings

from agir.donations.form_fields import AskAmountField
from agir.loans.forms import LenderForm, LoanForm
from agir.municipales.models import CommunePage
from agir.municipales.tasks import notify_commune_changed


class CommunePageForm(forms.ModelForm):
    def __init__(self, *args, person, **kwargs):
        super(CommunePageForm, self).__init__(*args, **kwargs)

        self.person = person

        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Modifier"))
        self.helper.layout = Layout(
            Fieldset("Informations sur la liste", "tete_liste", "contact_email"),
            Fieldset("La liste sur internet", "twitter", "facebook", "website"),
            Fieldset(
                "Les informations pour les dons par chèque", "ordre_don", "adresse_don"
            ),
        )

    def save(self, commit=True):
        if self.has_changed():
            changed_data = {
                self.fields[name].label: (self[name].initial, self.cleaned_data[name])
                for name in self.changed_data
            }
            notify_commune_changed.delay(self.instance.id, self.person.id, changed_data)

        return super().save(commit)

    class Meta:
        model = CommunePage
        fields = (
            "tete_liste",
            "contact_email",
            "twitter",
            "facebook",
            "website",
            "ordre_don",
            "adresse_don",
        )


class MunicipalesAskAmountForm(LoanForm):
    def __init__(self, *args, campagne=None, **kwargs):
        super().__init__(*args, **kwargs)

        fields = [
            "label",
            "error_messages",
            "required",
            "amount_choices",
            "show_tax_credit",
        ]

        self.fields["amount"] = AskAmountField(
            min_value=campagne.get("min_value", settings.LOAN_MINIMUM),
            max_value=campagne.get("max_value", settings.LOAN_MAXIMUM),
            **{f: getattr(self.fields["amount"], f) for f in fields}
        )


class MunicipalesLenderForm(LenderForm):
    show_subscribed = False

    def __init__(self, *args, campagne=None, **kwargs):
        super().__init__(*args, **kwargs)

        if campagne is None:
            campagne = {}
        self.fields["amount"] = forms.IntegerField(
            min_value=campagne.get("min_value", settings.LOAN_MINIMUM),
            max_value=campagne.get("max_value", settings.LOAN_MAXIMUM),
            required=True,
            widget=forms.HiddenInput,
        )
