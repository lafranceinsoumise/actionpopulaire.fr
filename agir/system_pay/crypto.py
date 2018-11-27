import hmac
from hashlib import sha1
from django.conf import settings


def get_signature(data):
    field_names = sorted(
        field_name for field_name in data if field_name.startswith("vads_")
    )
    values = [str(data[field_name]) for field_name in field_names]
    values.append(settings.SYSTEMPAY_CERTIFICATE)
    msg = "+".join(values)

    return sha1(msg.encode("utf-8")).hexdigest()


def check_signature(data):
    return hmac.compare_digest(get_signature(data), data["signature"])
