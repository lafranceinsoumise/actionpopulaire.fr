from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Row, Submit, Layout, Fieldset, Div
from django import forms

from agir.lib.form_components import HalfCol
from agir.municipales.models import CommunePage


class CommunePageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CommunePageForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Modifier"))
        self.helper.layout = Layout(
            Fieldset("Informations sur la liste", "tete_liste", "contact_email"),
            Fieldset("La liste sur internet", "twitter", "facebook", "website"),
            Fieldset(
                "Les informations pour les dons par chèque", "ordre_don", "adresse_don"
            ),
        )

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
