from django.core import validators
from django.core.exceptions import ValidationError
from django.db.models import JSONField
from django.db.models.fields.json import KeyTextTransform
from phonenumber_field import formfields
from phonenumber_field.modelfields import PhoneNumberDescriptor, PhoneNumberField
from phonenumber_field.phonenumber import to_python

from agir.lib.geo import FRENCH_COUNTRY_CODES


class MandatesField(JSONField):
    pass


class ValidatedPhoneNumberDescriptor(PhoneNumberDescriptor):
    def __init__(self, field, validation_field_name, unverified_value):
        super().__init__(field)
        self.validation_field_name = validation_field_name
        self.unverified_value = unverified_value

    def __set__(self, instance, value):
        value = to_python(value) or ""

        if instance.__dict__.get(self.field.name) != value:
            instance.__dict__[self.field.name] = value
            instance.__dict__[self.validation_field_name] = self.unverified_value


class PhoneNumberFormField(formfields.PhoneNumberField):
    def to_python(self, value):
        phone_number = to_python(value, region=self.region)

        if phone_number in validators.EMPTY_VALUES:
            return self.empty_value

        if phone_number and not phone_number.is_valid():
            if self.region == "FR":
                # As django-phonenumber-field does not support validation of
                # french overseas territories numbers when region defaults to 'FR',
                # we try to validate the phone number against all these territories
                # country codes to see if one matches before returning a validation
                # error.
                for country_code in FRENCH_COUNTRY_CODES:
                    phone_number = to_python(value, country_code)
                    if phone_number.is_valid():
                        self.region = country_code
                        return phone_number

            raise ValidationError(self.error_messages["invalid"])

        return phone_number


class ValidatedPhoneNumberField(PhoneNumberField):
    def __init__(self, *args, **kwargs):
        self.validated_field_name = kwargs.pop("validated_field_name")
        self.unverified_value = kwargs.pop("unverified_value")
        super().__init__(*args, **kwargs)

    def descriptor_class(self, _):
        return ValidatedPhoneNumberDescriptor(
            self, self.validated_field_name, self.unverified_value
        )

    def deconstruct(self):
        (name, path, [], keywords) = super().deconstruct()

        keywords.update(
            {
                "validated_field_name": self.validated_field_name,
                "unverified_value": self.unverified_value,
            }
        )
        return (name, path, [], keywords)

    def formfield(self, **kwargs):
        return super().formfield(form_class=PhoneNumberFormField, **kwargs)


class NestableKeyTextTransform:
    """
    Chainable version of django.db.models.fields.KeyTextTransform
    """

    def __new__(cls, field, *path):
        if not path:
            raise ValueError("Path must contain at least one key.")
        head, *tail = path
        field = KeyTextTransform(head, field)
        for head in tail:
            field = KeyTextTransform(head, field)
        return field
