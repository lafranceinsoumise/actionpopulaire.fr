from datetime import datetime

from data_france.models import Commune
from django import forms
from django.contrib import admin
from django.utils import timezone
from phonenumber_field.formfields import PhoneNumberField

from agir.api.admin import admin_site
from agir.elus.models import MandatMunicipal
from agir.people.models import Person, PersonEmail


class CreerMandatForm(forms.ModelForm):
    nom = forms.CharField(label="Nom", required=False)
    prenom = forms.CharField(label="Prénom", required=False)
    contact_phone = PhoneNumberField(label="Numéro de téléphone", required=False)
    email_officiel = forms.ModelChoiceField(
        label="Email officiel", queryset=PersonEmail.objects.none(), required=False
    )
    new_email = forms.EmailField(label="Ajouter un email officiel", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "person" in self.fields:
            person = self.get_initial_for_field(self.fields["person"], "person")
            self.fields["person"].required = False
            self.fields[
                "person"
            ].help_text = "Attention, si vous ne choisissez pas de personne, cela créera une nouvelle personne."
        else:
            person = self.instance.person

        if person is not None:
            self.fields["nom"].initial = person.last_name
            self.fields["prenom"].initial = person.first_name
            self.fields["contact_phone"].initial = person.contact_phone
            self.fields["email_officiel"].queryset = person.emails.all()

        if "email_officiel" not in self._meta.fields:
            del self.fields["email_officiel"]

    def clean(self):
        person = self.cleaned_data.get("person")
        new_email = self.cleaned_data.get("new_email")
        email_officiel = self.cleaned_data.get("email_officiel")

        if not person and not new_email:
            self.add_error(
                None,
                "Sélectionnez un compte existant ou indiquez l'adresse email pour créer un"
                " nouveau compte.",
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
                        "Cette adresse email est déjà associée à une autre personne.",
                    )

        if new_email and not person:
            try:
                person = Person.objects.get_by_natural_key(new_email)
            except Person.DoesNotExist:
                pass
            else:
                self.cleaned_data["person"] = person
                del self.cleaned_data["new_email"]

        if email_officiel and person and email_officiel.person != person:
            self.cleaned_data["email_officiel"] = None

        return self.cleaned_data

    def _save_m2m(self):
        super()._save_m2m()

        cleaned_data = self.cleaned_data
        person = cleaned_data["person"]

        if not person:
            # création d'une personne
            self.instance.person = Person.objects.create_person(
                cleaned_data["new_email"],
                first_name=cleaned_data.get("prenom", ""),
                last_name=cleaned_data.get("nom", "nom"),
                contact_phone=cleaned_data.get("contact_phone"),
            )
            self.instance.email_officiel = self.instance.person.primary_email
            self.instance.save()

        else:
            if "person" not in self.changed_data:
                person.first_name = cleaned_data["prenom"]
                person.last_name = cleaned_data["nom"]
                person.contact_phone = cleaned_data["contact_phone"]
                person.save(update_fields=["first_name", "last_name", "contact_phone"])

            if "new_email" in self.changed_data:
                person.add_email(cleaned_data["new_email"])
                email = PersonEmail.objects.get_by_natural_key(
                    cleaned_data["new_email"]
                )
                if email.person == person:
                    self.instance.email_officiel = email
                    self.instance.save(update_fields=["email_officiel"])


@admin.register(MandatMunicipal, site=admin_site)
class MandatMunicipalAdmin(admin.ModelAdmin):
    form = CreerMandatForm

    fieldsets = (
        (None, {"fields": ("person", "commune", "mandat")}),
        (
            "Informations sur l'élu⋅e",
            {"fields": ("nom", "prenom", "contact_phone", "email_officiel")},
        ),
        (
            "Précisions sur le mandat",
            {"fields": ("debut", "fin", "delegations_municipales", "communautaire")},
        ),
    )

    list_display = ("commune", "person", "mandat", "actif", "communautaire")
    readonly_fields = ("actif",)
    autocomplete_fields = ("person", "commune")

    def actif(self, obj):
        return obj.debut <= timezone.now() <= obj.fin

    actif.short_description = "Actif"

    def add_view(self, request, form_url="", extra_context=None):
        self.fieldsets = tuple(
            (
                title,
                {
                    **params,
                    "fields": tuple(
                        f for f in params["fields"] if f != "email_officiel"
                    ),
                },
            )
            for title, params in self.fieldsets
        )

        print(self.fieldsets)

        return super().add_view(request, form_url=form_url, extra_context=extra_context)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        self.readonly_fields = (*self.readonly_fields, "person")
        return super().change_view(request, object_id, form_url, extra_context)

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)

        if "person" in request.GET:
            try:
                initial["person"] = Person.objects.get(pk=request.GET["person"])
                initial["nom"] = initial["person"].last_name
                initial["prenom"] = initial["person"].first_name
            except Person.DoesNotExist:
                pass

        if "commune" in request.GET:
            try:
                initial["commune"] = Commune.objects.get(code=request.GET["commune"])
            except Commune.DoesNotExist:
                pass

        if "debut" in request.GET:
            try:
                initial["debut"] = datetime.strptime(request.GET["debut"], "%Y-%m-%d")
            except ValueError:
                pass

        if "fin" in request.GET:
            try:
                initial["fin"] = datetime.strptime(request.GET["fin"], "%Y-%m-%d")
            except ValueError:
                pass

        return initial
