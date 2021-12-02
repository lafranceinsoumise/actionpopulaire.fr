from collections import defaultdict

from phonenumber_field.phonenumber import PhoneNumber
from phonenumbers.phonenumberutil import number_type, PhoneNumberType


OVERSEAS_PREFIXES = {
    262: ["262", "269", "639", "692", "693"],  # Réunion and Mayotte
    590: ["590", "690", "691"],  # Guadeloupe, Saint-Martin, Saint Barthélemy
    594: ["594", "694"],  # Guyane
    596: ["596", "696", "727"],  # Martinique
}

TOM_COUNTRY_CODES = {
    687,  # Nouvelle-Calédonie
    689,  # Polynésie française
    508,  # Saint-Pierre-et-Miquelon
    681,  # Wallis-et-Futuna
}

OVERSEAS_MAPPING_PREFIXES = defaultdict(
    lambda: 33,
    {
        prefix: code
        for code, prefixes in OVERSEAS_PREFIXES.items()
        for prefix in prefixes
    },
)

FRENCH_COUNTRY_CODES = {33, *TOM_COUNTRY_CODES, *OVERSEAS_PREFIXES.keys()}


def normalize_overseas_numbers(phone_number):
    """if `phone_number` is an oversea phone number, returns its normal form

    For example, +33 6 90 00 12 34 (a mobile phone in Guadeloupe in its French form) is turned
    into +590 6 90 00 12 34 with the actual international prefix for Guadeloupe, which is what
    SMS senders are expecting.

    :param phone_number: a phone number to normalize
    :return: the normalized phone number
    """
    if phone_number.country_code == 33:
        p = PhoneNumber.from_string(phone_number.as_e164)  # cloning phone number
        p.country_code = OVERSEAS_MAPPING_PREFIXES[str(p.national_number)[:3]]
        return p

    return phone_number


def is_mobile_number(phone_number):
    """ "Check if `phone_number` is a French phone number

    :param phone_number:
    :return: a boolean
    """
    return number_type(phone_number) == PhoneNumberType.MOBILE


def is_french_number(phone_number):
    return phone_number.country_code in FRENCH_COUNTRY_CODES


def is_hexagonal_number(phone_number):
    return normalize_overseas_numbers(phone_number).country_code == 33
