from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext_lazy
from django_countries import countries
from rest_framework import serializers

from agir.lib.iban import IBAN, BIC


class ListValidatorMixin:
    def compare(self, cleaned_value, limit_value):
        compare = super().compare
        compares = [compare(value, limit_value) for value in cleaned_value]
        return any(compares)


class MinValueListValidator(ListValidatorMixin, validators.MinValueValidator):
    message = _("Ensure all values are greater than or equal to %(limit_value)s.")
    pass


class MaxValueListValidator(ListValidatorMixin, validators.MaxValueValidator):
    message = _("Ensure all values are less than or equal to %(limit_value)s.")
    pass


class DaysDeltaValidatorMixin:
    def clean(self, x):
        delta = max(x) - min(x)
        return delta.days

    def compare(self, cleaned_value, limit_value):
        # Avoid validating delta if only one value is specified
        return cleaned_value != 0 and super().compare(cleaned_value, limit_value)


@deconstructible
class MinDaysDeltaValidator(DaysDeltaValidatorMixin, validators.MinValueValidator):
    message = ngettext_lazy(
        "Ensure the difference between the biggest and smallest value is at least one day.",
        "Ensure the difference between the biggest and smallest value is at least %(limit_value)d days.",
        "limit_value",
    )
    code = "min_delta"


@deconstructible
class MaxDaysDeltaValidator(DaysDeltaValidatorMixin, validators.MaxValueValidator):
    message = ngettext_lazy(
        "Ensure the difference between the biggest and smallest value is less than one day.",
        "Ensure the difference between the biggest and smallest value is less than %(limit_value)d days.",
        "limit_value",
    )
    code = "max_delta"


@deconstructible
class FileSizeValidator:
    message = _(
        "Ce fichier est trop gros. Seuls les fichiers de moins de %(max_size)s sont acceptés."
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


@deconstructible
class AllowedCountriesValidator:
    message = _(
        "Seuls les comptes des pays suivants sont autorisés : {allowed_countries}."
    )
    code = "invalid_country"
    validation_error_class = forms.ValidationError

    def __init__(self, allowed_countries=None):
        self.allowed_countries = allowed_countries

    def __call__(self, value):
        if self.allowed_countries and value.country not in self.allowed_countries:
            message = self.message.format(
                allowed_countries=", ".join(
                    countries.name(code) or code for code in self.allowed_countries
                )
            )
            raise self.validation_error_class(message, self.code)


validate_allowed_countries = AllowedCountriesValidator()


@deconstructible
class IBANValidator:
    message = _(
        "Votre IBAN n'est pas au format correct. Un IBAN comprend entre 14 et 34 caractères (27 pour un compte français),"
        " commence par deux lettres correspondant au code du pays de votre compte ('FR' pour la France) et se"
        " présente généralement groupé par blocs de 4 caractères."
    )
    code = "invalid"
    validation_error_class = forms.ValidationError

    def __call__(self, iban):
        if not isinstance(iban, IBAN):
            iban = IBAN(iban)
        if not iban.is_valid():
            raise self.validation_error_class(self.message, self.code)


validate_iban = IBANValidator()


@deconstructible
class BICValidator:
    message = _(
        "Votre BIC n'est pas au format correct. Le BIC comprend 8 ou 11 caractères et chiffres."
    )
    code = "invalid"
    validation_error_class = forms.ValidationError

    def __call__(self, bic):
        if not isinstance(bic, BIC):
            bic = BIC(bic)
        if not bic.is_valid():
            raise self.validation_error_class(self.message, self.code)


validate_bic = BICValidator()


class AllowedCountriesSerializerValidator(AllowedCountriesValidator):
    validation_error_class = serializers.ValidationError


class IBANSerializerValidator(IBANValidator):
    validation_error_class = serializers.ValidationError


class BICSerializerValidator(BICValidator):
    validation_error_class = serializers.ValidationError
