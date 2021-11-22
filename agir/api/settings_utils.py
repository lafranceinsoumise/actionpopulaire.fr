import os

import re
from typing import Optional, Union, Pattern, List, Tuple

from django.core.exceptions import ImproperlyConfigured


def BOOLEAN(envvar: str, default: bool = False) -> bool:
    val = os.environ.get(envvar, "").lower()

    if val in ["y", "o", "yes", "oui", "true"]:
        return True
    elif val in ["n", "no", "non", "false"]:
        return False
    elif val:
        raise ImproperlyConfigured(
            f"Valeur incorrecte pour le paramètre booléen '{envvar}'."
        )

    return default


def STRING(
    envvar: str, default: str = None, regex: Optional[Union[str, Pattern]] = None
) -> str:
    value = os.environ.get(envvar, default)

    if regex:
        regex = re.compile(regex)
        match = regex.search(value)
        if not match:
            raise ImproperlyConfigured(f"Valeur incorrecte pour la chaîne '{envvar}")
        elif regex.groups == 1:
            value = match.group(1)
        elif regex.groups > 1:
            value = match.groups()

    return value


def STRING_ARRAY(
    envvar: str,
    separator: str,
    default: Optional[List] = None,
    regex: Optional[Union[str, Pattern]] = None,
) -> Union[List[str], List[Tuple[str, ...]]]:
    if default is None:
        default = []
    if envvar not in os.environ:
        return default
    value = os.environ.get(envvar, None)

    if value is None or value == "":
        return []

    values = value.split(separator)

    if regex:
        # ensure it is a regex
        regex = re.compile(regex)
        matches = [re.search(regex, v) for v in values]
        if any(m is None for m in matches):
            raise ImproperlyConfigured(f"Valeur incorrecte pour le tableau '{envvar}'")

        if regex.groups == 1:
            values = [m.group(1) for m in matches]
        elif regex.groups > 1:
            values = [m.groups() for m in matches]

    return values


def INTEGER(envvar, default=None):
    if envvar not in os.environ:
        return default

    val = os.environ[envvar]

    try:
        return int(val)
    except ValueError:
        raise ImproperlyConfigured(f"Valeur incorrecte pour l'entier '{envvar}'")
