import logging
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from prometheus_client import Counter

from agir.lib.utils import get_client_ip
from agir.people.models import PersonValidationSMS

from agir.lib.token_bucket import TokenBucket
from agir.people.tasks import send_validation_sms

RATE_LIMITED_1_MINUTE_MESSAGE = _(
    "Vous êtes limités à un SMS toutes les minutes, merci de bien vouloir patienter quelques secondes."
)
RATE_LIMITED_MESSAGE = _(
    "Vous avez déjà demandé plusieurs SMS : merci de bien vouloir patienter jusqu'à réception."
)

logger = logging.getLogger(__name__)


# short terms bucket: make sure maximum 1 SMS is sent every minute
ShortPhoneNumberBucket = TokenBucket("SMSShortPhoneNumber", 1, 60)
ShortPersonBucket = TokenBucket("SMSShortPerson", 1, 60)


def _initialize_buckets():
    global PhoneNumberBucket, PersonBucket, IPBucket
    PhoneNumberBucket = TokenBucket(
        "SMSPhoneNumber", settings.SMS_BUCKET_MAX, settings.SMS_BUCKET_INTERVAL
    )
    PersonBucket = TokenBucket(
        "SMSPerson", settings.SMS_BUCKET_MAX, settings.SMS_BUCKET_INTERVAL
    )
    IPBucket = TokenBucket(
        "SMSIP", settings.SMS_BUCKET_IP_MAX, settings.SMS_BUCKET_IP_INTERVAL
    )


_initialize_buckets()


CodeValidationTokenBucket = TokenBucket("CodeValidation", 5, 60)


sms_counter = Counter("agir_sms_requested_total", "Number of SMS requested", ["result"])
code_counter = Counter(
    "agir_sms_code_checked_total", "Number of code verifications requested", ["result"]
)


class RateLimitedException(Exception):
    pass


def send_new_code(person, request):
    # testing short term token buckets
    if not ShortPhoneNumberBucket.has_tokens(
        person.contact_phone
    ) or not ShortPersonBucket.has_tokens(person.pk):
        raise RateLimitedException(RATE_LIMITED_1_MINUTE_MESSAGE)

    if not PersonBucket.has_tokens(person.pk):
        sms_counter.labels("person_limited").inc()
        raise RateLimitedException(RATE_LIMITED_MESSAGE)

    if not PhoneNumberBucket.has_tokens(person.contact_phone):
        sms_counter.labels("number_limited").inc()
        raise RateLimitedException(RATE_LIMITED_MESSAGE)

    if not IPBucket.has_tokens(get_client_ip(request)):
        sms_counter.labels("ip_limited").inc()
        raise RateLimitedException(RATE_LIMITED_MESSAGE)

    sms = PersonValidationSMS.objects.create(
        phone_number=person.contact_phone, person=person
    )
    formatted_code = sms.code[:3] + " " + sms.code[3:]

    if not settings.SMS_DISABLED:
        send_validation_sms.delay(sms.id)
        sms_counter.labels("sent").inc()

    return formatted_code


def is_valid_code(person, code):
    if not CodeValidationTokenBucket.has_tokens(person.contact_phone):
        code_counter.labels("rate_limited").inc()
        raise RateLimitedException()
    try:
        # possible race condition here
        # TODO put delay in config variable
        person_code = PersonValidationSMS.objects.get(
            code=code, person=person, created__gt=timezone.now() - timedelta(minutes=30)
        )
        if person_code.phone_number != person.contact_phone:
            code_counter.labels("failure").inc()
            return False

        code_counter.labels("success").inc()
        return True
    except PersonValidationSMS.DoesNotExist:
        code_counter.labels("failure").inc()
        return False
