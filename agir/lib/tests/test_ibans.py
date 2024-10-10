from django import forms
from django.db.models import F
from django.test import TestCase

from schwifty import IBAN

from agir.lib.form_fields import IBANField
from agir.lib.iban import to_iban
from agir.lib.tests.models import IBANTestModel
from agir.lib.validators import IBANAllowedCountriesValidator

# generated on http://randomiban.com/
GOOD_IBANS = [
    "NL28ABNA4217631642",
    "SE1231949817743316221177",
    "FR3130066119293675223821795",
    "BA931022251637263927",
]

BAD_IBANS = [
    "ZEAIOJZAODAZOI",
    "78923798274982798",
    "298902 JOII 2IJOJIO23",
    "1234",
    "FR7612345678901276327382893289283923898290382",
]


class IBANTestCase(TestCase):
    def test_invalid_ibans(self):
        for iban in BAD_IBANS:
            self.assertFalse(to_iban(iban).is_valid)

    def test_valid_ibans(self):
        for iban in GOOD_IBANS:
            self.assertTrue(to_iban(iban).is_valid)


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


class IBANForm(forms.Form):
    iban = IBANField(label="IBAN")


class IBANFormFieldTestCase(TestCase):
    def test_validate_correct_ibans(self):
        for iban in GOOD_IBANS:
            form = IBANForm(data={"iban": iban})
            self.assertTrue(form.is_valid())

    def test_has_error_invalid_ibans(self):
        for iban in BAD_IBANS:
            form = IBANForm(data={"iban": iban})
            self.assertFalse(form.is_valid())
            self.assertTrue(form.has_error("iban", code="invalid"))

    def test_has_error_if_absent_when_required(self):
        form = IBANForm(data={})
        form.fields["iban"].required = True
        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error("iban", code="required"))

        form = IBANForm(data={"iban": ""})
        form.fields["iban"].required = True
        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error("iban", code="required"))

    def test_validates_if_absent_when_not_required(self):
        form = IBANForm(data={})
        form.fields["iban"].required = False
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["iban"], "")

    def test_validates_when_country_is_allowed(self):
        form = IBANForm(data={"iban": "FR3130066119293675223821795"})
        form.fields["iban"].validators.append(IBANAllowedCountriesValidator(["FR"]))
        self.assertTrue(form.is_valid())

    def test_has_error_when_country_is_not_allowed(self):
        form = IBANForm(data={"iban": "FR3130066119293675223821795"})
        form.fields["iban"].validators.append(IBANAllowedCountriesValidator(["SE"]))
        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error("iban", code="invalid_country"))
