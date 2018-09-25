import logging

import ovh
from django.conf import settings


logger = logging.getLogger(__name__)

client = ovh.Client(
    endpoint='ovh-eu',
    application_key=settings.OVH_APPLICATION_KEY,
    application_secret=settings.OVH_APPLICATION_SECRET,
    consumer_key=settings.OVH_CONSUMER_KEY,
)


class SMSSendException(Exception):
    pass


def send_sms(message, phone_number):
    try:
        result = client.post('/sms/' + settings.OVH_SMS_SERVICE + '/jobs',
                             charset='UTF-8',
                             coding='7bit',
                             receivers=[phone_number.as_e164],
                             message=message,
                             noStopClause=True,
                             priority='high',
                             sender='Fi',
                             validityPeriod=2880
                             )
    except Exception:
        logger.exception('Le message n\'a pas été envoyé.')
        raise SMSSendException('Le message n\'a pas été envoyé.')

    if len(result['invalidReceivers']) > 0:
        logger.error(f"Destinataires invalides {' '.join(result['invalidReceivers'])}")
        raise SMSSendException('Destinataire invalide.')

    if len(result['validReceivers']) < 1:
        raise SMSSendException('Le message n\'a pas été envoyé.')
