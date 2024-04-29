import traceback

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from agir.lib.admin.form_fields import AdminJsonWidget
from agir.lib.form_fields import AdminRichEditorWidget
from agir.lib.forms import CoordinatesFormMixin
from agir.lib.google_sheet import (
    parse_sheet_link,
    check_sheet_permissions,
)
from agir.people.models import Person, PersonEmail
from agir.people.person_forms.actions import (
    validate_custom_fields,
    get_people_form_class,
)
from agir.people.person_forms.models import PersonForm
from agir.people.person_forms.schema import schema


class PersonAdminForm(CoordinatesFormMixin, forms.ModelForm):
    newsletters = forms.MultipleChoiceField(
        label="Inscription aux lettres",
        choices=Person.Newsletter.choices,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    disabled_account = forms.BooleanField(
        label="Compte désactivé",
        required=False,
        help_text="Une personne dont le compte est désactivé ne pourra plus se connecter avec ses adresses email.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "disabled_account" in self.fields:
            if self.instance.role:
                self.fields["disabled_account"].initial = (
                    not self.instance.role.is_active
                )
            else:
                self.fields["disabled_account"].disabled = True

        self.fields["primary_email"] = forms.ModelChoiceField(
            self.instance.emails.all(),
            initial=self.instance.primary_email,
            required=False,
            label="Email principal",
        )

        if "public_email" in self.fields:
            self.fields["public_email"].queryset = self.instance.emails.all()

    def clean(self):
        cleaned_data = super().clean()
        if not "primary_email" in cleaned_data or "primary_email" in self.errors:
            raise ValidationError(
                "Adresse principale : veuillez indiquer une adresse e-mail valide"
            )
        if len(self.instance.emails.all()) == 0:
            try:
                PersonEmail.objects.get_by_natural_key(
                    address=self.cleaned_data["primary_email"]
                )
                raise ValidationError(
                    "Adresse principale : l'adresse e-mail est déjà associée à une autre personne"
                )
            except PersonEmail.DoesNotExist:
                pass

        return cleaned_data

    def _save_m2m(self):
        super()._save_m2m()

        if self.cleaned_data["primary_email"] != self.instance.primary_email:
            self.instance.set_primary_email(self.cleaned_data["primary_email"])

        if "disabled_account" in self.fields and self.instance.role:
            role = self.instance.role
            role.is_active = not self.cleaned_data["disabled_account"]
            role.save()

    class Meta:
        fields = "__all__"


def strip_all_keys(value):
    if isinstance(value, list):
        return [strip_all_keys(v) for v in value]
    if isinstance(value, dict):
        return {k.strip(): strip_all_keys(v) for k, v in value.items()}
    return value


class PersonFormSandboxForm(forms.ModelForm):
    class Meta:
        model = PersonForm
        fields = ["custom_fields"]
        widgets = {
            "custom_fields": AdminJsonWidget(schema=schema),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Submit(
                "top-preview",
                "Mettre à jour l'aperçu",
                css_class="btn-sm",
            ),
            "custom_fields",
            Submit("bottom-preview", "Mettre à jour l'aperçu"),
        )

    def save(self, commit=True):
        # Just return the instance without saving it
        return self.instance

    def clean_custom_fields(self):
        value = self.cleaned_data["custom_fields"]
        # Strip toutes les clés de tous les dictionnaires !
        value = strip_all_keys(value)
        validate_custom_fields(value)
        return value

    def _post_clean(self):
        super()._post_clean()
        try:
            klass = get_people_form_class(self.instance)
            klass()
        except Exception:
            self.add_error(
                None,
                ValidationError(
                    format_html(
                        "<p>{message}</p><pre>{stacktrace}</pre>",
                        message="Problème de création du formulaire. L'exception suivante a été rencontrée :",
                        stacktrace=traceback.format_exc(),
                    )
                ),
            )


class PersonFormForm(forms.ModelForm):
    class Meta:
        fields = "__all__"
        widgets = {
            "description": AdminRichEditorWidget(),
            "confirmation_note": AdminRichEditorWidget(),
            "custom_fields": AdminJsonWidget(schema=schema),
            "config": AdminJsonWidget(),
        }
        help_texts = {
            "lien_feuille_externe": mark_safe(
                f"Google Sheet uniquement pour le moment. La feuille doit être partagée"
                f" en écriture avec l'utilisateur <em>{settings.GCE_ACCOUNT_EMAIL}</em>."
            )
        }

    def clean_custom_fields(self):
        value = self.cleaned_data["custom_fields"]

        # Strip toutes les clés de tous les dictionnaires !
        value = strip_all_keys(value)

        validate_custom_fields(value)

        return value

    def clean_lien_feuille_externe(self):
        lien = self.cleaned_data["lien_feuille_externe"]

        if lien:
            id = parse_sheet_link(lien)

            if not id:
                raise ValidationError(
                    "Il ne s'agit pas de l'URL d'un tableau Google sheet."
                )

            check_sheet_permissions(id)

        return lien

    def _post_clean(self):
        super()._post_clean()

        try:
            klass = get_people_form_class(self.instance)
            klass()
        except Exception:
            self.add_error(
                None,
                ValidationError(
                    format_html(
                        "<p>{message}</p><pre>{stacktrace}</pre>",
                        message="Problème de création du formulaire. L'exception suivante a été rencontrée :",
                        stacktrace=traceback.format_exc(),
                    )
                ),
            )


class AddPersonEmailForm(forms.Form):
    email = forms.EmailField(label="Adresse email à ajouter", required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.add_input(Submit("ajouter", "Ajouter"))


class ChoosePrimaryAccount(forms.Form):
    primary_account = forms.ModelChoiceField(
        label="Compte principal", required=True, queryset=Person.objects.all()
    )

    def __init__(self, *args, persons, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["primary_account"].choices = [
            ("", "Choisir le compte principal")
        ] + [(p.id, p.email) for p in persons]

        self.helper = FormHelper()
        self.helper.add_input(Submit("fusionner", "Fusionner les comptes"))
