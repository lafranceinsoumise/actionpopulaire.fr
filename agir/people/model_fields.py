from django.contrib.postgres.fields import JSONField
from phonenumber_field.modelfields import PhoneNumberDescriptor, PhoneNumberField
from phonenumber_field.phonenumber import to_python


from . import form_fields


class MandatesField(JSONField):
    def formfield(self, **kwargs):
        defaults = {'form_class': form_fields.MandatesField}
        defaults.update(kwargs)
        return super().formfield(**defaults)


class ValidatedPhoneNumberDescriptor(PhoneNumberDescriptor):
    def __init__(self, field, validation_field_name, unverified_value):
        super().__init__(field)
        self.validation_field_name = validation_field_name
        self.unverified_value = unverified_value

    def __set__(self, instance, value):
        value = to_python(value) or ''

        if instance.__dict__.get(self.field.name) != value:
            instance.__dict__[self.field.name] = value
            instance.__dict__[self.validation_field_name] = self.unverified_value


class ValidatedPhoneNumberField(PhoneNumberField):
    def __init__(self, *args, **kwargs):
        self.validated_field_name = kwargs.pop('validated_field_name')
        self.unverified_value = kwargs.pop('unverified_value')
        super().__init__(*args, **kwargs)

    def descriptor_class(self, _):
        return ValidatedPhoneNumberDescriptor(self, self.validated_field_name, self.unverified_value)

    def deconstruct(self):
        (name, path, [], keywords) = super().deconstruct()

        keywords.update({'validated_field_name': self.validated_field_name, 'unverified_value': self.unverified_value})
        return (name, path, [], keywords)
