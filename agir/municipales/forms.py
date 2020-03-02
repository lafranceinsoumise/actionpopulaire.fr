from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Row, Div
from django import forms
from django.conf import settings
from django.utils.html import format_html
from phonenumber_field.formfields import PhoneNumberField

from agir.donations.form_fields import AskAmountField
from agir.lib.form_mixins import french_zipcode_validator, HalfCol
from agir.loans.forms import LenderForm, LoanForm
from agir.municipales import tasks
from agir.municipales.models import CommunePage
from agir.municipales.tasks import notify_commune_changed
from agir.people.models import Person
from agir.people.tasks import send_confirmation_email


class CommunePageForm(forms.ModelForm):
    def __init__(self, *args, person, **kwargs):
        super(CommunePageForm, self).__init__(*args, **kwargs)

        self.person = person

        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Modifier"))
        self.helper.layout = Layout(
            Fieldset("Informations sur la liste", "contact_email", "mandataire_email"),
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
            "mandataire_email",
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
            **{f: getattr(self.fields["amount"], f) for f in fields},
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


class ProcurationForm(forms.Form):
    nom = forms.CharField(label="Nom", required=True)
    prenom = forms.CharField(label="Prénom", required=True)
    code_postal = forms.CharField(
        label="Code postal", required=True, validators=[french_zipcode_validator]
    )
    email = forms.EmailField(label="Adresse email de contact", required=True)
    phone = PhoneNumberField(label="Numéro de téléphone", required=True)

    bureau = forms.CharField(
        label="Numéro de votre bureau de vote",
        required=False,
        help_text=format_html(
            'Le numéro de bureau figure sur votre carte électorale, ou <a href="{url}">vous pouvez l\'obtenir sur service-public.fr</a>',
            url="https://www.service-public.fr/particuliers/vosdroits/services-en-ligne-et-formulaires/ISE",
        ),
    )

    autres = forms.CharField(
        label="Avez-vous d'autres informations ou remarques ?",
        required=False,
        help_text="Indiquez toute autre information pertinente pour établir votre procuration.",
        widget=forms.Textarea,
    )

    subscribed = forms.BooleanField(
        label="Je souhaite recevoir les informations de la France insoumise dans ma boîte email.",
        required=False,
        widget=forms.CheckboxInput,
    )

    def __init__(self, *args, instance, person, **kwargs):
        super().__init__(*args, **kwargs)
        self.commune_id = instance.id
        self.person = person

        self.helper = FormHelper()
        self.helper.add_input(Submit("envoyer", "Envoyer aux équipes de la liste"))
        self.helper.layout = Layout(
            Row(HalfCol("nom"), HalfCol("prenom")),
            Row(
                HalfCol("email"),
                Div("phone", css_class="col-md-4"),
                Div("code_postal", css_class="col-md-2"),
            ),
            "bureau",
            "autres",
            "subscribed",
        )

        if self.person and self.person.subscribed:
            del self.fields["subscribed"]
            self.helper.layout.fields.remove("subscribed")

    def save(self):
        tasks.send_procuration_email.delay(
            commune_id=self.commune_id,
            nom_complet=f'{self.cleaned_data["prenom"]} {self.cleaned_data["nom"]}',
            email=self.cleaned_data["email"],
            phone=self.cleaned_data["phone"].as_international,
            bureau=self.cleaned_data["bureau"],
            autres=self.cleaned_data["autres"],
        )

        if self.person or self.cleaned_data["subscribed"]:
            if not self.person:
                try:
                    person = Person.objects.get_by_natural_key(
                        self.cleaned_data["email"]
                    )
                except Person.DoesNotExist:
                    send_confirmation_email.delay(
                        email=self.cleaned_data["email"],
                        location_zip=self.cleaned_data["code_postal"],
                        first_name=self.cleaned_data["prenom"],
                        last_name=self.cleaned_data["nom"],
                        contact_phone=self.cleaned_data["phone"].as_e164,
                    )
                    return
            else:
                person = self.person

            if self.cleaned_data.get("subscribed"):
                person.subscribed = True
            if not person.location_zip:
                person.location_zip = self.cleaned_data["code_postal"]
            if not person.first_name:
                person.first_name = self.cleaned_data["prenom"]
            if not person.last_name:
                person.last_name = self.cleaned_data["nom"]
            if not person.contact_phone:
                person.contact_phone = self.cleaned_data["phone"]
            person.save()


class CostCertificateForm(forms.Form):
    nom_liste = forms.CharField(label="Nom de la liste")
    mandataire_nom = forms.CharField(label="Nom et prénom du ou de la mandataire")
    mandataire_adresse = forms.CharField(
        label="Adresse complète du ou de la mandataire",
        widget=forms.Textarea(attrs={"rows": 4}),
    )
    nombre = forms.IntegerField(label="Nombre de tracts distribués")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("envoyer", "Télécharger le certificat"))
