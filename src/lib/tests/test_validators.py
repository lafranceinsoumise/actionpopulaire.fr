from unittest import TestCase
from rest_framework.serializers import ValidationError
from .. import validators


class MaxLengthValidatorTestCase(TestCase):
    def setUp(self):
        self.validator10 = validators.MaxLengthValidator(10)
        self.validator5 = validators.MaxLengthValidator(5)

        self.str5 = 'a' * 5
        self.str10 = 'a' * 10
        self.list5 = [True] * 5
        self.list10 = [True] * 10


    def test_correct_values(self):
        str5 = 'a' * 5
        str10 = 'a' * 10
        list5 = [True] * 5
        list10 = [True] * 10

        self.validator5(self.str5)
        self.validator5(self.list5)

        self.validator10(self.str5)
        self.validator10(self.str10)
        self.validator10(self.list5)
        self.validator10(self.list10)

    def test_incorrect_values(self):
        with self.assertRaises(ValidationError):
            self.validator5(self.str10)

        with self.assertRaises(ValidationError):
            self.validator5(self.list10)
