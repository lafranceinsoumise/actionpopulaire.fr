from django.test import TestCase
from math import ceil

import agir.lib.sms.ovh
from agir.lib.sms.common import (
    compute_sms_length_information,
    MESSAGE_LENGTH,
    SMSSendException,
)
from agir.lib.sms import send_bulk_sms


def _mock_send_sms(message, recipients, at=None, sender=None):
    """Mock send_sms function that pretends that +33 7 numbers are invalid"""
    if _mock_send_sms.counter is not None:
        _mock_send_sms.counter -= 1
        if _mock_send_sms.counter == 0:
            raise SMSSendException("Erreur incroyable")

    recipients = [r.as_e164 for r in recipients]

    return (
        [r for r in recipients if not r.startswith("+337")],
        [r for r in recipients if r.startswith("+337")],
    )


_mock_send_sms.counter = None


class SMSLengthTestCase(TestCase):
    def test_can_identify_character_set(self):
        res = compute_sms_length_information(
            "Simple SMS sans caractère spécial hors GSM7. Il doit faire quatre-vingt-huit caractères."
        )

        self.assertEqual(res, MESSAGE_LENGTH("GSM7", ceil(88 * 7 / 8), 1))

        res = compute_sms_length_information(
            "Ici j'ajoute juste des caractères spéciaux étendus genre {€^}. En tout quatre-vingt-huit"
        )

        self.assertEqual(res, MESSAGE_LENGTH("GSM7-EXT", ceil((88 + 4) * 7 / 8), 1))

        res = compute_sms_length_information(
            "Enfin ici ça va dépoter avec du UTF16 ŸÔâ. Cinquante-sept"
        )
        self.assertEqual(res, MESSAGE_LENGTH("UCS-2", 57 * 2, 1))


class SMSSendingTestCase(TestCase):
    def setUp(self) -> None:
        from agir.lib import sms

        self.original_send_sms = agir.lib.sms.SMS_PROVIDER.send_sms
        self.original_bulk_group_size = sms.SMS_PROVIDER.BULK_GROUP_SIZE

        agir.lib.sms.SMS_PROVIDER.send_sms = _mock_send_sms
        sms.SMS_PROVIDER.BULK_GROUP_SIZE = 2

    def tearDown(self) -> None:
        from agir.lib import sms

        agir.lib.sms.SMS_PROVIDER.send_sms = self.original_send_sms
        sms.BULK_GROUP_SIZE = self.original_bulk_group_size
        del self.original_send_sms
        del self.original_bulk_group_size

    def test_can_send_mass_sms(self):
        sent, invalid = send_bulk_sms(
            "mon message", ["+33678956454", "+33754986598", "+33678451252"]
        )

        self.assertEqual(sent, {"+33678956454", "+33678451252"})
        self.assertEqual(invalid, {"+33754986598"})
