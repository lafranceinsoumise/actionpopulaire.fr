from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.template.defaultfilters import filesizeformat
from django.utils.deconstruct import deconstructible
from django.utils.translation import ugettext as _

from phonenumber_field.formfields import PhoneNumberField

from agir.lib.form_fields import DateTimePickerWidget

from ..models import Person

all_person_field_names = [field.name for field in Person._meta.get_fields()]


class NotRequiredByDefaultMixin:
    def __init__(self, *args, required=False, **kwargs):
        super().__init__(*args, required=required, **kwargs)


class LongTextField(forms.CharField):
    widget = forms.Textarea


class DateTimeField(forms.DateTimeField):
    widget = DateTimePickerWidget


class ChoiceField(forms.ChoiceField):
    def __init__(self, *, choices, default_label=None, required=True, **kwargs):
        if default_label is None:
            default_label = (
                "---" if required else _("Non applicable / ne souhaite pas répondre")
            )

        choices = [("", default_label), *choices]

        super().__init__(choices=choices, required=required, **kwargs)


class MultipleChoiceField(NotRequiredByDefaultMixin, forms.MultipleChoiceField):
    widget = forms.CheckboxSelectMultiple


class BooleanField(NotRequiredByDefaultMixin, forms.BooleanField):
    pass


@deconstructible
class FileSizeValidator:
    message = _(
        "Ce fichier est trop gros. Seuls les fichiers de moins de %(max_size) sont acceptés."
    )
    code = "file_too_big"

    def __init__(self, max_size, message=None, code=None):
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code
        self.max_size = max_size

    def __call__(self, value):
        if value.size > self.max_size:
            raise ValidationError(
                self.message,
                code=self.code,
                params={"max_size": filesizeformat(self.max_size)},
            )


class FileField(forms.FileField):
    def __init__(
        self, *, max_size=None, allowed_extensions=None, validators=None, **kwargs
    ):
        validators = validators or []
        if allowed_extensions:
            validators.append(FileExtensionValidator(allowed_extensions))
        if max_size:
            validators.append(FileSizeValidator(max_size))

        super().__init__(validators=validators, **kwargs)


FIELDS = {
    "short_text": forms.CharField,
    "long_text": LongTextField,
    "choice": ChoiceField,
    "multiple_choice": MultipleChoiceField,
    "email_address": forms.EmailField,
    "phone_number": PhoneNumberField,
    "url": forms.URLField,
    "file": FileField,
    "boolean": BooleanField,
    "integer": forms.IntegerField,
    "decimal": forms.DecimalField,
    "datetime": DateTimeField,
}


def is_actual_model_field(field_descriptor):
    return (
        field_descriptor.get("person_field", False)
        and field_descriptor["id"] in all_person_field_names
    )


def get_form_field(field_descriptor: dict, is_edition=False):
    field_descriptor = field_descriptor.copy()
    field_type = field_descriptor.pop("type")
    field_descriptor.pop("id")
    field_descriptor.pop("person_field", None)
    editable = field_descriptor.pop("editable", False)
    if is_edition:
        field_descriptor["disabled"] = not editable
    if is_edition and not editable:
        field_descriptor["help_text"] = (
            field_descriptor.get("help_text", "")
            + " Ce champ ne peut pas être modifié."
        )

    klass = FIELDS.get(field_type)

    if klass:
        return klass(**field_descriptor)

    raise ValueError(f"Unkwnown field type: '{field_type}'")


def get_data_from_submission(s):
    data = s.data
    fields = s.form.fields_dict

    model_fields = {k for k in data if k in fields and is_actual_model_field(fields[k])}

    return {
        **{
            k: get_form_field(fields[k]).to_python(v) if k in fields else v
            for k, v in data.items()
            if k not in model_fields
        },
        **{
            k: Person._meta.get_field(k).formfield().to_python(data[k])
            for k in model_fields
        },
    }
