import struct
import base64
import hmac
import hashlib
from datetime import date

from django.conf import settings
from django.utils import timezone

REFERENCE_DATE = date(2017, 1, 1)
GROUP_ID_SIZE = 6
SIGNATURE_SIZE = 6
DIGESTMOD = hashlib.sha1
BASE64ENC = base64.urlsafe_b64encode


__all__ = ["get_next_promo_code"]


def generate_date_fragment(expiration_date):
    """Generate a two-character encoding of the expiration date

    That encoding is done that way:
    * Compute the number of days since the REFERENCE_DATE
    * encode it as two bytes (low-endian)
    * left shift the second byte by four bits

    It should now look that way (second hexdigit of second byte is all zero after left shift) :
    xxxx xxxx    xxxx 0000
    Only twelve bits of data ==> can be encoded by two base64 characters

    * Encode it in base64 and keep the two first characters

    :param expiration_date: a date corresponding to the day the promo code should expire
    :return: base64 encoding of the input date (bytes object)
    """
    days = (expiration_date - REFERENCE_DATE).days
    assert (
        days < 4096
    )  # 2^12 or the maximum value that can be set in 2 Base64 characters

    # use little-endian for packing
    b = bytearray(struct.pack("<I", days)[:2])
    b[1] <<= 4

    return BASE64ENC(b)[:2]


def generate_msg_part_for_group(group, expiration_date):
    """Generate the msg part of the promo code for a specific group

    The msg part is made of :

    * the expiration date (as 2 base64 characters)
    * 6 characters corresponding to the support group id

    :param group: the group for which the promo code must be generated
    :param expiration_date: the expiration date for the promo code
    :return:
    """
    date_fragment = generate_date_fragment(expiration_date)

    # let's hash the group part to make sure it works whatever the uuid generation mode
    # keep only the strictly minimum number of bytes
    keep_bytes = (GROUP_ID_SIZE * 3 // 4) + 1
    group_bytes = DIGESTMOD(group.pk.bytes).digest()[:keep_bytes]

    # let's use the first GROUP_ID_SIZE characters of the base64 encoding
    group_fragment = BASE64ENC(group_bytes)[:GROUP_ID_SIZE]

    return date_fragment + group_fragment


def sign_code(msg):
    keep_bytes = (SIGNATURE_SIZE * 3 // 4) + 1
    sig_bytes = hmac.new(
        key=settings.PROMO_CODE_KEY, msg=msg, digestmod=DIGESTMOD
    ).digest()[:keep_bytes]

    signature_frag = BASE64ENC(sig_bytes)[:SIGNATURE_SIZE]

    return msg + signature_frag


def generate_code_for_group(group, expiration_date):
    msg = generate_msg_part_for_group(group, expiration_date)
    return sign_code(msg).decode("ascii")


def get_next_promo_code(group):
    today = timezone.now().astimezone(timezone.get_default_timezone())

    if today.month == 12:
        expiration_date = date(today.year + 1, 1, 1)
    else:
        expiration_date = date(today.year, today.month + 1, 1)

    return generate_code_for_group(group, expiration_date)


def is_promo_code_delayed():
    today = timezone.now()
    return (
        settings.PROMO_CODE_DELAY is not None
        and settings.PROMO_CODE_DELAY.year == today.year
        and settings.PROMO_CODE_DELAY.month == today.month
        and today < (settings.PROMO_CODE_DELAY + timezone.timedelta(days=1))
    )


def next_promo_code_date():
    return settings.PROMO_CODE_DELAY + timezone.timedelta(days=1)
