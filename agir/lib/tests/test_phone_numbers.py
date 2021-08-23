from django.test import TestCase
from phonenumber_field.phonenumber import PhoneNumber

from agir.lib.phone_numbers import (
    is_mobile_number,
    is_french_number,
    is_hexagonal_number,
    normalize_overseas_numbers,
)


def p(phone_number):
    return PhoneNumber.from_string(phone_number, "FR")


class PhoneNumbersTestCase(TestCase):
    def test_is_mobile(self):
        self.assertTrue(is_mobile_number(p("06 38 68 98 45")))

        self.assertTrue(is_mobile_number(p("07 34 98 56 78")))

        self.assertFalse(is_mobile_number(p("06 90 48 25 64")))  # Guadeloupe, en +33

        self.assertTrue(
            is_mobile_number(p("+590 6 90 48 25 64"))  # Guadeloupe, en +590
        )

        self.assertFalse(is_mobile_number(p("01 42 87 65 89")))

        self.assertFalse(is_mobile_number(p("09 45 87 65 23")))

        self.assertFalse(is_mobile_number(p("05 90 45 78 56")))  # Guadeloupe, en +33

        self.assertFalse(
            is_mobile_number(p("+590 5 90 45 78 56"))  # Guadeloupe, en +590
        )

    def test_is_french(self):
        self.assertTrue(is_french_number(p("06 38 68 98 45")))

        self.assertTrue(is_french_number(p("01 48 68 98 45")))

        self.assertTrue(is_french_number(p("04 84 65 98 78")))

        self.assertTrue(is_french_number(p("05 90 56 45 12")))  # Guadeloupe, en +33

        self.assertTrue(is_french_number(p("+262 2 60 45 78 45")))  # Réunion, en +262

        self.assertFalse(is_french_number(p("+44 7554 456245")))

    def test_is_hexagonal(self):
        self.assertTrue(is_hexagonal_number(p("06 38 68 98 45")))

        self.assertTrue(is_hexagonal_number(p("01 48 68 98 45")))

        self.assertTrue(is_hexagonal_number(p("04 84 65 98 78")))

        self.assertFalse(is_hexagonal_number(p("05 90 56 45 12")))  # Guadeloupe, en +33

        self.assertFalse(
            is_hexagonal_number(p("+262 2 60 45 78 45"))  # Réunion, en +262
        )

        self.assertFalse(is_hexagonal_number(p("+44 7554 456245")))

    def test_normalize_overseas_number(self):
        self.assertEqual(
            normalize_overseas_numbers(p("+33 6 35 68 97 81")), p("+33 6 35 68 97 81")
        )

        self.assertEqual(
            normalize_overseas_numbers(p("+33 4 54 45 12 45")), p("+33 4 54 45 12 45")
        )

        self.assertEqual(
            normalize_overseas_numbers(p("+33 5 90 68 97 81")), p("+590 5 90 68 97 81")
        )

        self.assertEqual(
            normalize_overseas_numbers(p("+44 7554 456245")), p("+44 7554 456245")
        )

        self.assertEqual(
            normalize_overseas_numbers(p("+33 6 90 68 97 81")), p("+590 6 90 68 97 81")
        )
