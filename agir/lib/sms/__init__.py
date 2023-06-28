import logging

from django.conf import settings
from phonenumbers import number_type, PhoneNumberType

from agir.lib.sms import ovh, sfr
from agir.lib.sms.common import SMSSendException, to_phone_number, SMSException
from agir.lib.utils import grouper

logger = logging.getLogger(__name__)

SMS_PROVIDERS = {"OVH": ovh, "SFR": sfr}
SMS_PROVIDER = SMS_PROVIDERS.get(settings.SMS_PROVIDER)


def _send_sms_as_email(message, recipient, **params):
    """
    Sends an email with the message parameters to allow locally debugging
    through Mailhog

    :param message:
    :param recipient:
    :param params:
    :return:
    """
    import json
    import textwrap
    from django.core.mail import get_connection, EmailMultiAlternatives

    connection = get_connection()
    with connection:
        msg = "\n".join(textwrap.wrap(message, width=70))
        email = EmailMultiAlternatives(
            connection=connection,
            from_email="SMS message",
            subject=message,
            to=[recipient],
            body=f"\nSMS message sent to {recipient}"
            f"\n\n{'=' * 80}\n{msg}\n{'=' * 80}"
            f"\n\n{len(message)} characters"
            f"\n\nParameters:\n{json.dumps(params, indent=2)}",
        )
        email.send()


def send_sms(message, phone_number, force=False, at=None, sender=None):
    try:
        phone_number = to_phone_number(phone_number)

        if not force and not phone_number.is_valid():
            raise SMSSendException(
                "Le numéro ne semble pas correct", invalid=[phone_number]
            )

        if not force and number_type(phone_number) not in [
            PhoneNumberType.FIXED_LINE_OR_MOBILE,
            PhoneNumberType.MOBILE,
        ]:
            raise SMSSendException(
                "Le numéro ne semble pas être un numéro de mobile",
                invalid=[phone_number],
            )

        if settings.DEBUG:
            _send_sms_as_email(message, phone_number, at=at, sender=sender)

        valid, invalid = SMS_PROVIDER.send_sms(
            message, [phone_number], at=at, sender=sender
        )

        if len(invalid) > 0:
            raise SMSSendException("Destinataire invalide.", invalid=invalid)

        if len(valid) < 1:
            raise SMSSendException(
                "Le message n'a pas été envoyé.", invalid=[phone_number]
            )
    except SMSException as e:
        logger.exception(str(e))
        raise e


def send_bulk_sms(message, phone_numbers, at=None, sender=None):
    sent = set()
    not_sent = set()

    for numbers in grouper(phone_numbers, SMS_PROVIDER.BULK_GROUP_SIZE):
        recipients = [to_phone_number(number) for number in numbers]
        try:
            valid, invalid = SMS_PROVIDER.send_sms(
                message, recipients, at=at, sender=sender
            )
            sent.update(valid)
            not_sent.update(invalid)
        except SMSSendException as e:
            logger.exception(str(e))
            not_sent.update(recipients)

    return sent, not_sent
