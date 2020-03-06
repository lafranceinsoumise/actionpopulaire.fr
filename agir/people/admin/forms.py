import traceback

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.core.exceptions import ValidationError
from django.utils.html import format_html

from agir.lib.form_fields import AdminRichEditorWidget, AdminJsonWidget
from agir.lib.forms import CoordinatesFormMixin
from agir.people.models import Person
from agir.people.person_forms.actions import (
    validate_custom_fields,
    get_people_form_class,
)
from agir.people.person_forms.schema import schema


class PersonAdminForm(CoordinatesFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["primary_email"] = forms.ModelChoiceField(
            self.instance.emails.all(),
            initial=self.instance.primary_email,
            required=True,
            label="Email principal",
        )

    def _save_m2m(self):
        super()._save_m2m()

        if self.cleaned_data["primary_email"] != self.instance.primary_email:
            self.instance.set_primary_email(self.cleaned_data["primary_email"])

    class Meta:
        fields = "__all__"


def strip_all_keys(value):
    if isinstance(value, list):
        return [strip_all_keys(v) for v in value]
    if isinstance(value, dict):
        return {k.strip(): strip_all_keys(v) for k, v in value.items()}
    return value


class PersonFormForm(forms.ModelForm):
    class Meta:
        fields = "__all__"
        widgets = {
            "description": AdminRichEditorWidget(),
            "confirmation_note": AdminRichEditorWidget(),
            "custom_fields": AdminJsonWidget(schema=schema),
            "config": AdminJsonWidget(),
        }

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
