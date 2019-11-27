import logging
from uuid import UUID

from datetime import datetime
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.template.defaultfilters import filesizeformat
from django.utils.deconstruct import deconstructible
from django.utils.translation import ugettext as _
from django.utils.formats import localize_input

import iso8601

from phonenumber_field.formfields import PhoneNumberField

from agir.events.models import Event
from agir.lib.data import departements_choices, regions_choices
from agir.lib.form_fields import DateTimePickerWidget, SelectizeWidget, IBANField
from agir.lib.token_bucket import TokenBucket

from ..models import Person


logger = logging.getLogger(__name__)


all_person_field_names = [field.name for field in Person._meta.get_fields()]


class NotRequiredByDefaultMixin:
    def __init__(self, *args, required=False, **kwargs):
        super().__init__(*args, required=required, **kwargs)


class ShortTextField(forms.CharField):
    def __init__(self, *args, choices=None, **kwargs):
        if choices is not None:
            self.widget = SelectizeWidget(
                create=True,
                choices=[
                    (
                        "",
                        "Choisissez parmi les choix proposés ou tapez votre propre réponse.",
                    ),
                    *choices,
                ],
            )

        super().__init__(*args, **kwargs)


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


class AutocompleteChoiceField(ChoiceField):
    widget = SelectizeWidget


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


# In person form there is a token bucket for preventing searching
class PersonChoiceField(forms.ModelChoiceField):
    widget = forms.TextInput

    def __init__(self, *args, **kwargs):
        super().__init__(
            Person.objects.filter(role__is_active=True),
            help_text="Entrez l'adresse email d'une personne inscrite sur la plateforme.",
            to_field_name="emails__address",
            error_messages={
                "invalid_choice": "Cette adresse email ne correspond pas à une personne inscrite."
            },
            *args,
            **kwargs,
        )

    def to_python(self, value):
        if value in self.empty_values:
            return None

        return super().to_python(value).pk


FIELDS = {
    "short_text": ShortTextField,
    "long_text": LongTextField,
    "choice": ChoiceField,
    "autocomplete_choice": AutocompleteChoiceField,
    "multiple_choice": MultipleChoiceField,
    "email_address": forms.EmailField,
    "phone_number": PhoneNumberField,
    "url": forms.URLField,
    "file": FileField,
    "boolean": BooleanField,
    "integer": forms.IntegerField,
    "decimal": forms.DecimalField,
    "datetime": DateTimeField,
    "person": PersonChoiceField,
    "iban": IBANField,
}

PREDEFINED_CHOICES = {
    "departements": departements_choices,
    "regions": regions_choices,
    "organized_events": lambda instance: (
        (
            e.id,
            f"{e.name} ({localize_input(e.start_time, '%d/%m/%Y %H:%M')}) - {e.get_visibility_display()}",
        )
        for e in (
            instance.organized_events.exclude(visibility=Event.VISIBILITY_ADMIN)
            if instance is not None
            else Event.objects.exclude(visibility=Event.VISIBILITY_ADMIN)
        )
    ),
}


def event_from_value(uuid):
    try:
        UUID(uuid)
        return Event.objects.filter(id=uuid).first()
    except ValueError:
        return uuid


PREDEFINED_CHOICES_REVERSE = {"organized_events": event_from_value}


def is_actual_model_field(field_descriptor):
    return (
        field_descriptor.get("person_field", False)
        and field_descriptor["id"] in all_person_field_names
    )


def get_form_field(field_descriptor: dict, is_submission_edition=False, instance=None):
    field_descriptor = field_descriptor.copy()
    field_type = field_descriptor.pop("type")
    field_descriptor.pop("id")
    field_descriptor.pop("person_field", None)
    editable = field_descriptor.pop("editable", False)
    if is_submission_edition:
        field_descriptor["disabled"] = not editable
    if is_submission_edition and not editable:
        field_descriptor["help_text"] = (
            field_descriptor.get("help_text", "")
            + " Ce champ ne peut pas être modifié."
        )

    klass = FIELDS.get(field_type)

    if "choices" in field_descriptor and isinstance(field_descriptor["choices"], str):
        choices = PREDEFINED_CHOICES.get(field_descriptor["choices"])
        field_descriptor["choices"] = (
            choices if not callable(choices) else choices(instance)
        )

    if klass:
        return klass(**field_descriptor)

    raise ValueError(f"Unkwnown field type: '{field_type}'")


def form_value_to_python(field_descriptor, value):
    if field_descriptor is None:
        return value

    if field_descriptor.get("type") == "datetime":
        try:
            return iso8601.parse_date(value)
        except iso8601.ParseError:
            logger.info(
                "Cannot parse date from field '%s' : '%s'",
                field_descriptor.get("id"),
                value,
            )
            return str(value)
    elif field_descriptor.get("type") == "file":
        return value

    field_instance = get_form_field(field_descriptor, is_submission_edition=False)
    try:
        return field_instance.to_python(value)
    except ValidationError:
        logger.info(
            "Cannot parse field '%s' of type '%s' : '%s''",
            field_descriptor.get("id"),
            field_descriptor.get("type"),
            value,
        )
        return str(value)


def get_data_from_submission(s):
    data = s.data
    fields = s.form.fields_dict

    model_fields = {k for k in data if k in fields and is_actual_model_field(fields[k])}

    return {
        **{
            k: form_value_to_python(fields.get(k), v)
            for k, v in data.items()
            if k not in model_fields
        },
        **{
            k: Person._meta.get_field(k).formfield().to_python(data[k])
            for k in model_fields
        },
    }
