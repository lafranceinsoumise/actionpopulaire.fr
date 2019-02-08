from django.db.models import F
from django.test import TestCase

from agir.lib.iban import IBAN
from agir.lib.tests.models import IBANTestModel


class IBANTestCase(TestCase):
    def test_invalid_ibans(self):
        ibans = [
            "ZEAIOJZAODAZOI" "78923798274982798",
            "298902 JOII 2IJOJIO23",
            "1234",
            "FR7612345678901276327382893289283923898290382",
        ]

        for iban in ibans:
            self.assertFalse(IBAN(iban).is_valid())

    def test_valid_ibans(self):
        # generated on http://randomiban.com/
        ibans = [
            "NL28ABNA4217631642",
            "MZ65681166912998238935942",
            "SE1231949817743316221177",
            "FR3130066119293675223821795",
            "BA931022251637263927",
        ]

        for iban in ibans:
            self.assertTrue(IBAN(iban).is_valid())


class IBANModelFieldTestCase(TestCase):
    def setUp(self):
        self.instance = IBANTestModel.objects.create(iban="NL28 ABNA 4217 6316 42")

    def test_iban_is_well_formated_in_db(self):
        i = IBANTestModel.objects.annotate(raw_iban=F("iban")).get()
        self.assertEqual(i.raw_iban, "NL28ABNA4217631642")

    def test_get_iban_object(self):
        self.assertTrue(isinstance(self.instance.iban, IBAN))

    def test_can_set_iban_from_string(self):
        self.instance.iban = "FR31 3006 6119 2936 7522 3821 795"
        self.instance.save()

        self.instance.refresh_from_db()
        self.assertTrue(self.instance.iban, IBAN)
