from datetime import datetime

import reversion
from data_france.models import Commune, EPCI
from django import forms
from django.contrib import admin
from django.db import IntegrityError
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from phonenumber_field.formfields import PhoneNumberField

from agir.api.admin import admin_site
from agir.elus.models import MandatMunicipal, DELEGATIONS_CHOICES
from agir.people.models import Person, PersonEmail

PERSON_FIELDS = [
    "last_name",
    "first_name",
    "contact_phone",
    "is_insoumise",
    "subscribed",
]


class CreerMandatForm(forms.ModelForm):
    last_name = forms.CharField(label="Nom", required=False)
    first_name = forms.CharField(label="Prénom", required=False)
    contact_phone = PhoneNumberField(label="Numéro de téléphone", required=False)
    email_officiel = forms.ModelChoiceField(
        label="Email officiel", queryset=PersonEmail.objects.none(), required=False
    )
    is_insoumise = forms.BooleanField(label="Est insoumis⋅e", required=False)
    subscribed = forms.BooleanField(
        label="Inscrit à la lettre d'information de la FI",
        required=False,
        help_text="Assurez-vous d'avoir recueilli le consensus de la personne. Il n'est pas possible d'inscrire une"
        " personne sans avoir recueilli son consentement EXPLICITE.",
    )
    new_email = forms.EmailField(label="Ajouter un email officiel", required=False)
    delegations_municipales = forms.MultipleChoiceField(
        choices=DELEGATIONS_CHOICES,
        label="Délégations (pour un maire adjoint)",
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if hasattr(self.instance, "commune"):
            commune = self.instance.commune
            epci = commune.epci
            if epci:
                self.fields["communautaire"].label = f"Élu auprès de la {epci.nom}"
            else:
                self.fields["communautaire"].disabled = True

        if "person" in self.fields:
            person = self.get_initial_for_field(self.fields["person"], "person")
            self.fields["person"].required = False
            self.fields["person"].label = "Compte plateforme de l'élu"
            self.fields[
                "person"
            ].help_text = "Attention, si vous ne choisissez pas de compte plateforme, cela créera une fiche élu sans compte."
        else:
            person = getattr(self.instance, "person", None)

        if person is not None:
            for f in PERSON_FIELDS:
                self.fields[f].initial = getattr(person, f)
            self.fields["email_officiel"].queryset = person.emails.all()

        if "email_officiel" not in self._meta.fields:
            del self.fields["email_officiel"]

    def clean(self):
        if "person" in self.fields:
            person = self.cleaned_data.get("person")
        else:
            person = getattr(self.instance, "person", None)

        new_email = self.cleaned_data.get("new_email")
        contact_phone = self.cleaned_data.get("contact_phone")
        last_name = self.cleaned_data.get("last_name")
        first_name = self.cleaned_data.get("first_name")
        email_officiel = self.cleaned_data.get("email_officiel")

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
                self.cleaned_data["person"] = person
                del self.cleaned_data["new_email"]

        if email_officiel and person and email_officiel.person != person:
            self.cleaned_data["email_officiel"] = None

        return self.cleaned_data

    def _save_m2m(self):
        super()._save_m2m()

        cleaned_data = self.cleaned_data
        if "person" in self.fields:
            person = cleaned_data["person"]
        else:
            person = self.instance.person

        if not person:
            # création d'une personne
            self.instance.person = Person.objects.create_person(
                cleaned_data["new_email"],
                **{k: v for k, v in cleaned_data.items() if k in PERSON_FIELDS},
            )
            self.instance.email_officiel = self.instance.person.primary_email
            self.instance.save(update_fields=["email_officiel"])
        else:
            if "person" not in self.changed_data:
                for f in PERSON_FIELDS:
                    setattr(person, f, cleaned_data[f])

                person.save(update_fields=PERSON_FIELDS)

            if "new_email" in self.changed_data:
                try:
                    email = person.add_email(cleaned_data["new_email"])
                except IntegrityError:
                    pass
                else:
                    self.instance.email_officiel = email
                    self.instance.save(update_fields=["email_officiel"])

        return super()._save_m2m()


@admin.register(MandatMunicipal, site=admin_site)
class MandatMunicipalAdmin(admin.ModelAdmin):
    form = CreerMandatForm
    add_form_template = "admin/change_form.html"
    change_form_template = "elus/admin/change_form.html"

    list_filter = ("reseau",)

    fieldsets = (
        (None, {"fields": ("person", "commune", "mandat")}),
        (
            "Informations sur l'élu⋅e",
            {"fields": (*PERSON_FIELDS, "email_officiel", "new_email", "reseau",)},
        ),
        (
            "Précisions sur le mandat",
            {"fields": ("debut", "fin", "delegations_municipales", "communautaire")},
        ),
    )

    list_display = (
        "commune",
        "person",
        "mandat",
        "actif",
        "communautaire",
        "is_insoumise",
        "reseau",
    )
    readonly_fields = ("actif", "person_link")
    autocomplete_fields = ("person", "commune")

    def actif(self, obj):
        return "Oui" if (obj.debut <= timezone.now().date() <= obj.fin) else "Non"

    actif.short_description = "Mandat en cours"

    def person_link(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            reverse("admin:people_person_change", args=[obj.person_id]),
            str(obj.person),
        )

    person_link.short_description = "Personne"

    def is_insoumise(self, obj):
        if obj.person:
            return "Oui" if obj.person.is_insoumise else "Non"
        return "-"

    is_insoumise.short_description = "Insoumis⋅e"

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
        self.fieldsets = tuple(
            (
                (
                    title,
                    {
                        **params,
                        "fields": tuple(
                            f if f != "person" else "person_link"
                            for f in params["fields"]
                        ),
                    },
                )
                for title, params in self.fieldsets
            )
        )
        return super().change_view(request, object_id, form_url, extra_context)

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)

        if "person" in request.GET:
            try:
                initial["person"] = Person.objects.get(pk=request.GET["person"])
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

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        with reversion.create_revision():
            reversion.set_comment("Depuis l'interface d'aministration")
            reversion.set_user(request.user)
            return super().changeform_view(request, object_id, form_url, extra_context)
