from django.test import TestCase
from math import ceil

from agir.lib.sms import compute_sms_length_information, MessageLength


class SMSLengthTestCase(TestCase):
    def test_can_identify_character_set(self):
        res = compute_sms_length_information(
            "Simple SMS sans caractère spécial hors GSM7. Il doit faire quatre-vingt-huit caractères."
        )

        self.assertEqual(res, MessageLength("GSM7", ceil(88 * 7 / 8), 1))

        res = compute_sms_length_information(
            "Ici j'ajoute juste des caractères spéciaux étendus genre {€^}. En tout quatre-vingt-huit"
        )

        self.assertEqual(res, MessageLength("GSM7-EXT", ceil((88 + 4) * 7 / 8), 1))

        res = compute_sms_length_information(
            "Enfin ici ça va dépoter avec du UTF16 ŸÔâ. Cinquante-sept"
        )
        self.assertEqual(res, MessageLength("UCS-2", 57 * 2, 1))
