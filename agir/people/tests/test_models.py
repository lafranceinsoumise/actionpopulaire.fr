from unittest import mock

from django.test import TestCase, override_settings
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist

from agir.authentication.models import Role
from agir.people.models import Person, PersonEmail


class BasicPersonTestCase(TestCase):
    def test_can_create_user_with_email(self):
        user = Person.objects.create_person(email='test@domain.com')

        self.assertEqual(user.email, 'test@domain.com')
        self.assertEqual(user.pk, Person.objects.get_by_natural_key('test@domain.com').pk)

    @mock.patch('agir.people.models.metrics.subscriptions')
    def test_subscription_metric_is_called(self, subscriptions_metric):
        Person.objects.create_person(email='test@domain.com')

        subscriptions_metric.inc.assert_called_once()

    def test_can_add_email(self):
        user = Person.objects.create_person(email='test@domain.com')
        user.add_email('test2@domain.com', bounced=True)
        user.save()

        self.assertEqual(user.email, 'test@domain.com')
        self.assertEqual(user.emails.all()[1].address, 'test2@domain.com')
        self.assertEqual(user.emails.all()[1].bounced, True)

    def test_can_edit_email(self):
        user = Person.objects.create_person(email='test@domain.com')
        user.add_email('test@domain.com', bounced=True)

        self.assertEqual(user.emails.all()[0].bounced, True)

    def test_can_add_existing_email(self):
        user = Person.objects.create_person(email='test@domain.com')
        user.add_email('test@domain.com')

    def test_can_set_primary_email(self):
        user = Person.objects.create_person(email='test@domain.com')
        user.add_email('test2@domain.com')
        user.save()
        user.set_primary_email('test2@domain.com')

        self.assertEqual(user.email, 'test2@domain.com')
        self.assertEqual(user.emails.all()[1].address, 'test@domain.com')

    def test_cannot_set_non_existing_primary_email(self):
        user = Person.objects.create_person(email='test@domain.com')
        user.add_email('test2@domain.com')
        user.save()

        with self.assertRaises(ObjectDoesNotExist):
            user.set_primary_email('test3@domain.com')

    def test_can_create_user_with_password_and_authenticate(self):
        user = Person.objects.create_person('test1@domain.com', 'test')

        self.assertEqual(user.email, 'test1@domain.com')
        self.assertEqual(user, Person.objects.get_by_natural_key('test1@domain.com'))

        authenticated_user = authenticate(request=None, email='test1@domain.com', password='test')
        self.assertIsNotNone(authenticated_user)
        self.assertEqual(authenticated_user.type, Role.PERSON_ROLE)
        self.assertEqual(user, authenticated_user.person)

    def test_person_represented_by_email(self):
        person = Person.objects.create_person('test1@domain.com')

        self.assertEqual(str(person), 'test1@domain.com')

    @override_settings(MAILTRAIN_DISABLE=False)
    @mock.patch('agir.people.tasks.update_person_mailtrain')
    def test_person_is_updated_in_mailtrain(self, update_mailtrain):
        person = Person.objects.create_person('test1@domain.com')

        update_mailtrain.delay.assert_called_once()
        args = update_mailtrain.delay.call_args[0]
        self.assertEqual(args[0], person.pk)

    @override_settings(MAILTRAIN_DISABLE=False)
    @mock.patch('agir.people.tasks.update_person_mailtrain')
    @mock.patch('agir.people.tasks.delete_email_mailtrain')
    def test_email_is_deleted_from_mailtrain_when_email_deleted(self, delete_email_mailtrain, update_person_email):
        person = Person.objects.create_person('test1@domain.com')
        p2 = PersonEmail.objects.create(address='test2@domain.com', person=person)

        delete_email_mailtrain.reset_mock()

        address = p2.address
        p2.delete()

        delete_email_mailtrain.delay.assert_called_once()
        self.assertEqual(delete_email_mailtrain.delay.call_args[0][0], address)

