from django.test import TestCase

from django.contrib.auth import authenticate

from .models import Person


class BasicPersonTestCase(TestCase):
    def test_can_create_user_with_email(self):
        user = Person.objects.create(email='test@domain.com')

        self.assertEqual(user.email, 'test@domain.com')
        self.assertEqual(user.pk, Person.objects.get_by_natural_key('test@domain.com').pk)

    def test_can_create_user_with_password_and_authenticate(self):
        user = Person.objects.create_user('test1@domain.com', 'test')

        self.assertEqual(user.email, 'test1@domain.com')
        self.assertEqual(user, Person.objects.get_by_natural_key('test1@domain.com'))

        authenticated_user = authenticate(request=None, email='test1@domain.com', password='test')
        self.assertEqual(user, authenticated_user)

    def test_person_represented_by_email(self):
        person = Person.objects.create_user('test1@domain.com')

        self.assertEqual(str(person), 'test1@domain.com')
