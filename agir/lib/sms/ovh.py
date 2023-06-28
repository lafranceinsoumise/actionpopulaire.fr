from math import ceil

import ovh
from django.conf import settings
from django.utils import timezone

from agir.lib.sms.common import SMSSendException

client = ovh.Client(
    endpoint="ovh-eu",
    application_key=settings.OVH_APPLICATION_KEY,
    application_secret=settings.OVH_APPLICATION_SECRET,
    consumer_key=settings.OVH_CONSUMER_KEY,
)

BULK_GROUP_SIZE = 50


def send_sms(message, recipients, *, at=None, sender=None, **_):
    sender = sender if sender else settings.OVH_DEFAULT_SENDER
    params = dict(
        charset="UTF-8",
        coding="7bit",
        receivers=[recipient.as_e164 for recipient in recipients],
        message=message,
        noStopClause=True,
        priority="high",
        sender=sender,
        validityPeriod=2880,
    )

    if at is not None:
        now = timezone.now()
        if at <= now:
            raise SMSSendException("`at` est dans le passé")

        minutes = ceil((at - now).total_seconds() / 60)
        params["differedPeriod"] = minutes

    try:
        result = client.post("/sms/" + settings.OVH_SMS_SERVICE + "/jobs", **params)
        return result["validReceivers"], result["invalidReceivers"]
    except ovh.exceptions.APIError:
        raise SMSSendException("L'API OVH a rencontré une erreur", invalid=recipients)
    except Exception:
        raise SMSSendException("Le message n'a pas été envoyé.", invalid=recipients)
