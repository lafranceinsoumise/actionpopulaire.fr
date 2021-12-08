from django import forms
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class IBANValidator:
    message = _(
        "Votre IBAN n'est pas au correct. Un IBAN comprend entre 14 et 34 caractères (27 pour un compte français),"
        " commence par deux lettres correspondant au code du pays de votre compte ('FR' pour la France) et se"
        " présente généralement groupé par blocs de 4 caractères."
    )
    code = "invalid"

    def __call__(self, iban):
        if not iban.is_valid():
            raise forms.ValidationError(self.message, self.code)


validate_iban = IBANValidator()
