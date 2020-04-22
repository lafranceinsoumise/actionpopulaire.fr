import logging
from uuid import UUID

import iso8601
from data_france.models import Commune
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.forms.models import ModelChoiceIterator
from django.template.defaultfilters import filesizeformat
from django.utils.deconstruct import deconstructible
from django.utils.formats import localize_input
from django.utils.translation import ugettext as _
from phonenumber_field.formfields import PhoneNumberField
from webpack_loader import utils as webpack_loader_utils

from agir.events.models import Event
from agir.lib.data import departements_choices, regions_choices
from agir.lib.form_fields import DateTimePickerWidget, SelectizeWidget, IBANField
from ..models import Person
from ...groups.models import SupportGroup
from ...municipales.models import CommunePage

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
class PersonChoiceField(forms.CharField):
    widget = forms.TextInput

    default_error_messages = {
        "invalid_choice": _(
            "Cette adresse email ne correspond pas à une personne inscrite."
        )
    }

    def __init__(self, *args, allow_self=False, allow_inactive=False, **kwargs):
        kwargs.setdefault(
            "help_text",
            "Entrez l'adresse email d'une personne inscrite sur la plateforme.",
        )

        super().__init__(*args, **kwargs)
        self.allow_self = allow_self
        self.allow_inactive = allow_inactive

    def to_python(self, value):
        if value in self.empty_values:
            return None

        try:
            value = Person.objects.get_by_natural_key(value.strip())
        except Person.DoesNotExist:
            raise ValidationError(
                self.error_messages["invalid_choice"], code="invalid_choice"
            )

        if (
            not self.allow_inactive
            and value.role is not None
            and not value.role.is_active
        ):
            raise ValidationError(
                self.error_messages["invalid_choice"], code="invalid_choice"
            )

        return value.pk


class CommuneWidget(forms.Widget):
    template_name = "people/widgets/commune.html"

    def format_value(self, value):
        if value is None:
            return None

        return f"{value.type}-{value.code}"

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        if value is not None:
            context[
                "label"
            ] = f"{value.nom} ({value.code_departement}, {value.get_type_display()})"

        return context

    @property
    def media(self):
        return forms.Media(
            js=(webpack_loader_utils.get_files("people/communeField")[0]["url"],)
        )


class CommuneField(forms.CharField):
    widget = CommuneWidget

    def widget_attrs(self, widget):
        return {**super().widget_attrs(widget), "data-commune": "Y"}

    def commune(self, value):
        try:
            type, code = value.split("-")
            return Commune.objects.get(type=type, code=code)
        except (ValueError, Commune.DoesNotExist):
            raise ValidationError("Commune inconnue")

    def to_python(self, value):
        if value in self.empty_values:
            return None

        self.commune(value)

        return value

    def prepare_value(self, value):
        if value == "" or value is None:
            return None

        if isinstance(value, Commune):
            return value

        try:
            return self.commune(value)
        except ValidationError:
            return None


class GroupWidget(forms.Select):
    @property
    def media(self):
        if self.attrs.get("data-group-selector") == "Y":
            return forms.Media(
                js=(webpack_loader_utils.get_files("groups/groupSelector")[0]["url"],)
            )
        return forms.Media()


class ModelDefaultChoiceIterator(ModelChoiceIterator):
    def __init__(self, field):
        super().__init__(field)
        self.queryset = field.default_queryset


class GroupField(forms.ModelChoiceField):
    instance_in_kwargs = True
    widget = GroupWidget
    iterator = ModelDefaultChoiceIterator

    def __init__(
        self, *, instance, choices=None, default_options_label="Mes groupes", **kwargs
    ):
        queryset = SupportGroup.objects.active()
        self.default_queryset = queryset.filter(memberships__person_id=instance.id)

        if choices in ["animateur", "animator"]:
            queryset = self.default_queryset = SupportGroup.objects.filter(
                memberships__person_id=instance.id, memberships__is_referent=True
            )
        elif choices in ["membre", "member"]:
            queryset = self.default_queryset
        elif choices:
            raise ValueError(
                f"Valeur '{choices}' du paramètres choices incorrect: laissez vide ou indiquez 'member' ou 'animator'"
            )
        self.choice_constraint = choices
        self.default_options_label = default_options_label

        # Attention : exécuter à la fin, parce que super().__init__ initialise le widget, et lui assigne les
        # choix (donc besoin de default_queryset), et appelle widget_attrs (donc besoin de choice_constraint et
        # default_options_label
        super().__init__(queryset, **kwargs)

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        if self.choice_constraint is None:
            attrs["data-group-selector"] = "Y"
        if self.default_options_label:
            attrs["data-default-options-label"] = self.default_options_label
        return attrs

    def to_python(self, value):
        value = super().to_python(value)
        if value is None:
            return None
        return str(value.pk)


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
    "commune": CommuneField,
    "group": GroupField,
}

PREDEFINED_CHOICES = {
    "departements": departements_choices,
    "regions": regions_choices,
    "commune_pages": lambda instance: tuple(
        (commune.code, f"{commune.name} ({commune.code_departement})")
        for commune in CommunePage.objects.filter(published=True)
    ),
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


PREDEFINED_CHOICES_REVERSE = {
    "organized_events": event_from_value,
    "commune_pages": lambda code: CommunePage.objects.filter(code=code).first(),
}


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

    if (
        isinstance(field_descriptor.get("choices"), str)
        and field_descriptor["choices"] in PREDEFINED_CHOICES
    ):
        choices = PREDEFINED_CHOICES[field_descriptor["choices"]]
        field_descriptor["choices"] = (
            choices if not callable(choices) else choices(instance)
        )

    if klass:
        if getattr(klass, "instance_in_kwargs", False):
            return klass(**field_descriptor, instance=instance)
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
