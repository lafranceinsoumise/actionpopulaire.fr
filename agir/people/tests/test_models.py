from unittest import mock

from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase

from agir.authentication.models import Role
from agir.people.models import Person


class BasicPersonTestCase(TestCase):
    def test_can_create_user_with_email(self):
        user = Person.objects.create_insoumise(email="test@domain.com")

        self.assertEqual(user.email, "test@domain.com")
        self.assertEqual(
            user.pk, Person.objects.get_by_natural_key("test@domain.com").pk
        )

    def test_non_insoumise(self):
        user = Person.objects.create_political_support(email="test@domain.com")

        self.assertEqual(user.subscribed, False)

    @mock.patch("agir.people.models.metrics.subscriptions")
    def test_subscription_metric_is_called(self, subscriptions_metric):
        Person.objects.create_insoumise(email="test@domain.com")

        subscriptions_metric.inc.assert_called_once()

    def test_can_add_email(self):
        user = Person.objects.create_insoumise(email="test@domain.com")
        user.add_email("test2@domain.com", bounced=True)
        user.save()

        self.assertEqual(user.email, "test@domain.com")
        self.assertEqual(user.emails.all()[1].address, "test2@domain.com")
        self.assertEqual(user.emails.all()[1].bounced, True)

    def test_can_edit_email(self):
        user = Person.objects.create_insoumise(email="test@domain.com")
        user.add_email("test@domain.com", bounced=True)

        self.assertEqual(user.emails.all()[0].bounced, True)

    def test_can_add_existing_email(self):
        user = Person.objects.create_insoumise(email="test@domain.com")
        user.add_email("test@domain.com")

    def test_can_set_primary_email(self):
        user = Person.objects.create_insoumise(email="test@domain.com")
        user.add_email("test2@domain.com")
        user.save()
        user.set_primary_email("test2@domain.com")
        user.refresh_from_db()
        self.assertEqual(user.email, "test2@domain.com")
        self.assertEqual(user.emails.all()[1].address, "test@domain.com")

    def test_cannot_set_non_existing_primary_email(self):
        user = Person.objects.create_insoumise(email="test@domain.com")
        user.add_email("test2@domain.com")
        user.save()

        with self.assertRaises(ObjectDoesNotExist):
            user.set_primary_email("test3@domain.com")

    def test_can_create_user_with_password_and_authenticate(self):
        user = Person.objects.create_insoumise("test1@domain.com", "test")

        self.assertEqual(user.email, "test1@domain.com")
        self.assertEqual(user, Person.objects.get_by_natural_key("test1@domain.com"))

        authenticated_user = authenticate(
            request=None, email="test1@domain.com", password="test"
        )
        self.assertIsNotNone(authenticated_user)
        self.assertEqual(authenticated_user.type, Role.PERSON_ROLE)
        self.assertEqual(user, authenticated_user.person)

    def test_person_represented_by_email(self):
        person = Person.objects.create_insoumise("test1@domain.com")
        person.refresh_from_db()
        self.assertEqual(str(person), "(TE) <test1@domain.com>")

    def test_default_display_name_is_not_set_upon_creation_if_present(self):
        person = Person.objects.create_insoumise(
            "test1@domain.com", first_name="Jane", last_name="Doe", display_name="JJDD"
        )
        self.assertEqual(person.display_name, "JJDD")

    def test_default_display_name_is_set_upon_creation_based_on_full_name(self):
        person = Person.objects.create_insoumise(
            "test1@domain.com", first_name="Jane", last_name="Doe"
        )
        self.assertEqual(person.display_name, "JD")

    def test_default_display_name_is_set_upon_creation_based_on_first_name(self):
        person = Person.objects.create_insoumise("test1@domain.com", first_name="Jane")
        self.assertEqual(person.display_name, "JA")

    def test_default_display_name_is_set_upon_creation_based_on_last_name(self):
        person = Person.objects.create_insoumise("test1@domain.com", last_name="Doe")
        self.assertEqual(person.display_name, "DO")

    def test_default_display_name_is_set_upon_creation_based_on_email(self):
        person = Person.objects.create_insoumise("test1@domain.com")
        self.assertEqual(person.display_name, "TE")


class ContactPhoneTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_insoumise(
            email="test@domain.com", contact_phone="0612345678"
        )

    def test_unverified_contact_phone_by_default(self):
        self.assertEqual(
            self.person.contact_phone_status, Person.CONTACT_PHONE_UNVERIFIED
        )

    def test_unverified_when_changing_number(self):
        self.person.contact_phone_status = Person.CONTACT_PHONE_VERIFIED
        self.person.contact_phone = "0687654321"
        self.assertEqual(
            self.person.contact_phone_status, Person.CONTACT_PHONE_UNVERIFIED
        )

    def test_still_verified_when_changing_for_same_number(self):
        self.person.contact_phone_status = Person.CONTACT_PHONE_VERIFIED

        self.person.contact_phone = "0612345678"
        self.assertEqual(
            self.person.contact_phone_status, Person.CONTACT_PHONE_VERIFIED
        )

        self.person.contact_phone = "+33612345678"
        self.assertEqual(
            self.person.contact_phone_status, Person.CONTACT_PHONE_VERIFIED
        )
