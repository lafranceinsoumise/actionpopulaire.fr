from django import forms
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


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
        if not bic.is_valid():
            raise self.validation_error_class(self.message, self.code)


validate_bic = BICValidator()


class IBANSerializerValidator(IBANValidator):
    validation_error_class = serializers.ValidationError


class BICSerializerValidator(BICValidator):
    validation_error_class = serializers.ValidationError
