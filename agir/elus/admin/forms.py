from django import forms
from django.db import IntegrityError

from agir.elus.models import DELEGATIONS_CHOICES
from agir.people.models import PersonEmail, Person

PERSON_FIELDS = [
    "last_name",
    "first_name",
    "contact_phone",
    "location_address1",
    "location_address2",
    "location_zip",
    "location_city",
    "membre_reseau_elus",
    "commentaires",
]

creer_mandat_declared_fields = {
    f.name: f.formfield() for f in Person._meta.get_fields() if f.name in PERSON_FIELDS
}


class CreerMandatForm(forms.ModelForm):
    email_officiel = forms.ModelChoiceField(
        label="Email officiel", queryset=PersonEmail.objects.none(), required=False
    )
    subscribed_lfi = forms.BooleanField(
        label="Inscrit à la lettre d'information de la FI",
        required=False,
        help_text="Assurez-vous d'avoir recueilli le consensus de la personne. Il n'est pas possible d'inscrire une"
        " personne sans avoir recueilli son consentement EXPLICITE.",
    )
    new_email = forms.EmailField(label="Ajouter un email officiel", required=False)
    delegations = forms.MultipleChoiceField(
        choices=DELEGATIONS_CHOICES,
        label="Délégations (pour un maire adjoint ou un vice-président)",
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "person" in self.fields:
            self.fields["person"].label = "Compte plateforme de l'élu"
            # on retire les champs de personne
            for name in PERSON_FIELDS:
                del self.fields[name]

        else:
            person = getattr(self.instance, "person", None)

            if person is not None:
                for f in PERSON_FIELDS:
                    self.fields[f].initial = getattr(person, f)
                self.fields["email_officiel"].queryset = person.emails.all()
                self.fields["subscribed_lfi"].initial = (
                    Person.NEWSLETTER_LFI in person.newsletters
                )

        if "email_officiel" not in self._meta.fields:
            del self.fields["email_officiel"]

    def clean(self):
        cleaned_data = super().clean()

        if "person" in self.fields:
            person = cleaned_data.get("person")
        else:
            person = getattr(self.instance, "person", None)

        new_email = cleaned_data.get("new_email")
        contact_phone = cleaned_data.get("contact_phone")
        last_name = cleaned_data.get("last_name")
        first_name = cleaned_data.get("first_name")
        email_officiel = cleaned_data.get("email_officiel")

        minimal_information = (
            person or new_email or contact_phone or (last_name and first_name)
        )

        if not minimal_information:
            self.add_error(
                None,
                "Sélectionnez un compte existant ou indiquez adresse email, numéro de téléphone ou nom/prénom pour"
                " créer une fiche élue sans compte.",
            )

        if new_email and person:
            try:
                person_email = PersonEmail.objects.get_by_natural_key(new_email)
            except PersonEmail.DoesNotExist:
                pass
            else:
                if person_email.person != person:
                    self.add_error(
                        "new_email",
                        "Cette adresse email est déjà utilisée associée à quelqu'un d'autre sur la plateforme.",
                    )

        if new_email and not person:
            try:
                person = Person.objects.get_by_natural_key(new_email)
            except Person.DoesNotExist:
                pass
            else:
                cleaned_data["person"] = person
                del cleaned_data["new_email"]

        if email_officiel and person and email_officiel.person != person:
            cleaned_data["email_officiel"] = None

        return cleaned_data

    def save(self, commit=True):
        cleaned_data = self.cleaned_data
        if "person" in self.fields:
            person = cleaned_data["person"]
        else:
            person = getattr(self.instance, "person", None)

        if not person:
            # création d'une personne
            self.instance.person = Person.objects.create_person(
                cleaned_data["new_email"],
                **{k: v for k, v in cleaned_data.items() if k in PERSON_FIELDS},
            )
            self.instance.newsletters = (
                [Person.NEWSLETTER_LFI] if cleaned_data["subscribed_lfi"] else []
            )
            self.instance.email_officiel = self.instance.person.primary_email
        else:
            if "person" not in self.fields:
                if any(
                    f in self.changed_data for f in [*PERSON_FIELDS, "subscribed_lfi"]
                ):
                    for f in PERSON_FIELDS:
                        setattr(person, f, cleaned_data[f])
                    person.subscribed = cleaned_data["subscribed_lfi"]
                    person.save()

            if "new_email" in self.changed_data:
                try:
                    email = person.add_email(cleaned_data["new_email"])
                except IntegrityError:
                    pass
                else:
                    self.instance.email_officiel = email

        return super().save(commit=commit)


# Inspiré du code de DeclarativeFieldsMetaclass et ModelFormMetaclass
# base_fields et declared_fields semblent toujours etre le meme objet
creer_mandat_declared_fields.update(CreerMandatForm.declared_fields)
CreerMandatForm.base_fields = (
    CreerMandatForm.declared_fields
) = creer_mandat_declared_fields


class CreerMandatMunicipalForm(CreerMandatForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "communautaire" in self.fields:
            if self.instance.conseil is None or self.instance.conseil.epci is None:
                self.fields["communautaire"].disabled = True
            else:
                epci = self.instance.conseil.epci
                self.fields["communautaire"].label = f"Mandat auprès de la {epci.nom}"
