import logging

from django.core import validators
from schwifty import IBAN, BIC

logger = logging.getLogger(__name__)


def to_iban(s, validate=False):
    if isinstance(s, IBAN) or s in validators.EMPTY_VALUES:
        return s

    if not isinstance(s, str):
        s = str(s)

    return IBAN(s, allow_invalid=not validate, validate_bban=True)


def to_bic(s, validate=False):
    if isinstance(s, BIC) or s in validators.EMPTY_VALUES:
        return s

    if not isinstance(s, str):
        s = str(s)

    return BIC(s, allow_invalid=not validate)
