import traceback

from django import forms
from django.core.exceptions import ValidationError
from django.utils.html import format_html

from agir.lib.form_fields import AdminRichEditorWidget, AdminJsonWidget
from agir.lib.forms import CoordinatesFormMixin
from agir.people.person_forms.actions import (
    validate_custom_fields,
    get_people_form_class,
)


class PersonAdminForm(CoordinatesFormMixin, forms.ModelForm):
    pass


class PersonFormForm(forms.ModelForm):
    class Meta:
        fields = "__all__"
        widgets = {
            "description": AdminRichEditorWidget(),
            "confirmation_note": AdminRichEditorWidget(),
            "custom_fields": AdminJsonWidget(),
            "config": AdminJsonWidget(),
        }

    def clean_custom_fields(self):
        value = self.cleaned_data["custom_fields"]
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
