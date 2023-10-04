import re

from django import forms
from django.contrib.postgres.fields import ArrayField
from django.core import checks, exceptions
from django.core.validators import RegexValidator
from django.db import models
from django.utils.itercompat import is_iterable
from django.utils.translation import gettext_lazy as _

from agir.lib.form_fields import IBANField as FormIBANField
from agir.lib.iban import to_iban, IBAN, BIC_REGEX, to_bic, BIC
from agir.lib.utils import (
    validate_facebook_event_url,
    INVALID_FACEBOOK_EVENT_LINK_MESSAGE,
)
from agir.lib.validators import validate_iban


class IBANFieldDescriptor:
    def __init__(self, field):
        self.field = field

    def __get__(self, instance=None, owner=None):
        if instance is None:
            return self
        return instance.__dict__[self.field.name]

    def __set__(self, instance, value):
        instance.__dict__[self.field.name] = to_iban(value)


class IBANField(models.Field):
    description = _("IBAN identifiant un compte un banque")
    descriptor_class = IBANFieldDescriptor

    default_validators = [validate_iban]

    def __init__(self, *args, allowed_countries=None, **kwargs):
        self.allowed_countries = allowed_countries
        kwargs["max_length"] = 34

        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["allowed_countries"] = self.allowed_countries

        return name, path, args, kwargs

    def get_internal_type(self):
        return "CharField"

    def to_python(self, value):
        return to_iban(value)

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        value = self.to_python(value)

        if isinstance(value, IBAN):
            return value.as_stored_value
        return value

    def formfield(self, **kwargs):
        return super().formfield(
            **{
                "form_class": FormIBANField,
                "allowed_countries": self.allowed_countries,
                **kwargs,
            }
        )

    def contribute_to_class(self, cls, name, private_only=False):
        super().contribute_to_class(cls, name, private_only)
        setattr(cls, name, self.descriptor_class(self))

    def _check_allowed_countries(self):
        if not self.allowed_countries:
            return []

        if not is_iterable(self.allowed_countries):
            return [
                checks.Error(
                    "'allowed_countries' must be an iterable (e.g. a list or tuple)",
                    obj=self,
                    id="agir.lib.E001",
                )
            ]

        if not all(isinstance(s, str) and len(s) == 2 for s in self.allowed_countries):
            return [
                checks.Error(
                    "'allowed_countries' must be an iterable containing 2-letters country codes",
                    obj=self,
                    id="agir.lib.E002",
                )
            ]

        return []

    def check(self, **kwargs):
        return [*super().check(), *self._check_allowed_countries()]


class BICField(models.CharField):
    message = "Indiquez un BIC correct (8 ou 11 caractères et chiffres)."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, max_length=11, **kwargs)
        self.validators.append(
            RegexValidator(
                regex=BIC_REGEX,
                message=self.message,
            )
        )

    def get_internal_type(self):
        return "CharField"

    def to_python(self, value):
        return to_bic(value)

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        value = self.to_python(value)

        if isinstance(value, BIC):
            return value.as_stored_value

        return value

    def deconstruct(self):
        *res, keywords = super().deconstruct()
        del keywords["max_length"]
        return *res, keywords

    def formfield(self, **kwargs):
        kwargs["validators"] = (
            RegexValidator(regex=BIC_REGEX, message=self.message),
            *kwargs.get("validators", ()),
        )
        return super().formfield(**kwargs)


# https://gist.github.com/danni/f55c4ce19598b2b345ef
class ChoiceArrayField(ArrayField):
    def formfield(self, **kwargs):
        defaults = {
            "form_class": forms.MultipleChoiceField,
            "choices": self.base_field.choices,
        }
        defaults.update(kwargs)

        return super(ArrayField, self).formfield(**defaults)


class FacebookPageField(models.CharField):
    FACEBOOK_ID_RE = re.compile(
        r"^(?:(?:https://)?www.facebook.com/)?([a-zA-Z0-9.\-]{5,})(?:/.*)?$"
    )

    def to_python(self, value):
        if value in self.empty_values:
            return value

        value = self.FACEBOOK_ID_RE.match(value)
        if value:
            return value.group(1)
        else:
            raise exceptions.ValidationError(
                INVALID_FACEBOOK_EVENT_LINK_MESSAGE,
                params={"value": value},
            )


class FacebookEventField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 255)
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        if value in self.empty_values:
            return value

        facebook_value = validate_facebook_event_url(value)
        if not facebook_value:
            raise exceptions.ValidationError(
                INVALID_FACEBOOK_EVENT_LINK_MESSAGE,
                params={"value": value},
            )
        return facebook_value

    def formfield(self, **kwargs):
        defaults = {"max_length": 255}
        kwargs.update(defaults)
        return super().formfield(**defaults)


class TwitterProfileField(models.CharField):
    TWITTER_ID_RE = re.compile(r"^(?:@|https://twitter.com/)?([a-zA-Z0-9_]{1,15})$")

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 15)
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        if value in self.empty_values:
            return value

        value = self.TWITTER_ID_RE.match(value)
        if value:
            return value.group(1)
        else:
            raise exceptions.ValidationError(
                "Identifiant twitter incorrect (il ne peut comporter que des caractères alphanumériques et des tirets soulignants (_)",
                params={"value": value},
            )

    def formfield(self, **kwargs):
        defaults = {"max_length": 255}
        kwargs.update(defaults)
        return super().formfield(**defaults)
