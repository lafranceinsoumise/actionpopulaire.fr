from django.core import validators
from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _, ngettext_lazy


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
