import logging
from datetime import timedelta

import re

import ovh
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from prometheus_client import Counter

from agir.lib.token_bucket import TokenBucket
from agir.people.models import PersonValidationSMS

MOBILE_PHONE_RE = re.compile(r'^0[67]')

DROMS_PREFIX = {
    '639': 262,  # Mayotte
    '690': 590,  # Gadeloupe
    '691': 590,  # Gadeloupe
    '694': 594,  # Guyane
    '696': 596,  # Martinique
    '697': 596,  # Martinique
    '692': 262,  # Réunion
    '693': 262,  # Réunion
}

TOM_COUNTRY_CODES = {687, 689, 590, 590, 508, 681}
DROMS_COUNTRY_CODES = set(DROMS_PREFIX.values())

logger = logging.getLogger(__name__)


def normalize_mobile_phone(phone_number, messages):
    if phone_number.country_code == 33:
        # if french number, we verifies if it is not actually a DROM mobile number and replace country code in this case
        drom = DROMS_PREFIX.get(str(phone_number.national_number)[:3], None)
        if drom is not None:
            phone_number.country_code = drom
        # if it is not the case, we verify it is a mobile number
        elif not MOBILE_PHONE_RE.match(phone_number.as_national):
            raise ValidationError(messages['mobile_only'])

    elif phone_number.country_code in DROMS_COUNTRY_CODES:
        # if country code is one of the DROM country codes, we check that is is a valid mobile phone number
        if DROMS_PREFIX.get(str(phone_number.national_number)[:3], None) != phone_number.country_code:
            raise ValidationError(messages['mobile_only'])

    elif phone_number.country_code in TOM_COUNTRY_CODES:
        pass

    else:
        raise ValidationError(messages['french_only'])

    return phone_number


client = ovh.Client(
    endpoint='ovh-eu',
    application_key=settings.OVH_APPLICATION_KEY,
    application_secret=settings.OVH_APPLICATION_SECRET,
    consumer_key=settings.OVH_CONSUMER_KEY,
)

SMSShortTokenBucket = TokenBucket('SMSShort', 1, 60)
SMSLongTokenBucket = TokenBucket('SMSLong', settings.SMS_BUCKET_MAX, settings.SMS_BUCKET_INTERVAL)
SMSPersonTokenBucket = TokenBucket('SMSPerson', settings.SMS_IP_BUCKET_MAX, settings.SMS_BUCKET_INTERVAL)
CodeValidationTokenBucket = TokenBucket('CodeValidation', 5, 60)

sms_counter = Counter('agir_sms_requested_total', 'Number of SMS requested', ['result'])
code_counter = Counter('agir_sms_code_checked_total', 'Number of code verifications requested', ['result'])


class SMSSendException(Exception):
    pass


class SMSCodeBypassed(Exception):
    pass


class RateLimitedException(Exception):
    pass


def send(message, phone_number):
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


def send_new_code(person):
    if not SMSPersonTokenBucket.has_tokens(person.pk):
        sms_counter.labels('person_limited').inc()
        raise RateLimitedException('Trop de messages envoyés, réessayer dans quelques minutes.')

    if not (SMSShortTokenBucket.has_tokens(person.contact_phone) and SMSLongTokenBucket.has_tokens(person.contact_phone)):
        sms_counter.labels('number_limited').inc()
        raise RateLimitedException('Trop de messages envoyés, réessayer dans quelques minutes.')

    sms = PersonValidationSMS(phone_number=person.contact_phone, person=person)
    formatted_code = sms.code[:3] + ' ' + sms.code[3:]
    message = 'Votre code de validation pour votre compte France insoumise est {0}'.format(formatted_code)

    if not settings.OVH_SMS_DISABLE:
        send(message, person.contact_phone)
    sms_counter.labels('sent').inc()

    sms.save()
    return formatted_code


def is_valid_code(person, code):
    if not CodeValidationTokenBucket.has_tokens(person.contact_phone):
        code_counter.labels('rate_limited').inc()
        raise RateLimitedException()
    try:
        # possible race condition here
        # TODO put delay in config variable
        person_code = PersonValidationSMS.objects.get(code=code, person=person,
                                        created__gt=timezone.now() - timedelta(minutes=30))
        if person_code.phone_number != person.contact_phone:
            code_counter.labels('failure').inc()
            return False

        code_counter.labels('success').inc()
        return True
    except PersonValidationSMS.DoesNotExist:
        code_counter.labels('failure').inc()
        return False
