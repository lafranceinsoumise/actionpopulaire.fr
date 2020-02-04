from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset
from django import forms

from agir.loans.forms import LenderForm
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


class MunicipalesLenderForm(LenderForm):
    class Meta(LenderForm.Meta):
        # retire "subscribed"
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
