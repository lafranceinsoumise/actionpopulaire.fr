from django.test import TestCase
from rest_framework.test import APIRequestFactory, APITestCase
from rest_framework import status

from django.contrib.auth import authenticate

from .models import Person
from .viewsets import LegacyPersonViewSet


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


class LegacyPersonEndpointTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create(
            email='jean.georges@domain.com',
            first_name='Jean',
            last_name='Georges',
        )

        self.detail_view = LegacyPersonViewSet.as_view({
            'get': 'retrieve',
            'put': 'update',
            'patch': 'partial_update',
            'delete': 'destroy'
        })

        self.list_view = LegacyPersonViewSet.as_view({
            'get': 'list',
            'post': 'create'
        })

        self.factory = APIRequestFactory()

    def test_contain_simple_fields(self):
        request = self.factory.get('')
        response = self.detail_view(request, pk=self.person.pk)

        expected_fields = {'_id', 'id', 'email', 'first_name', 'last_name', 'bounced', 'bounced_date'}

        assert expected_fields.issubset(set(response.data))

    def test_return_correct_values(self):
        request = self.factory.get('')
        response = self.detail_view(request, pk=self.person.pk)

        self.assertEqual(self.person.email, response.data['email'])
        self.assertEqual(self.person.first_name, response.data['first_name'])
        self.assertEqual(self.person.last_name, response.data['last_name'])

    def test_can_post_new_person(self):
        request = self.factory.post('', data={
            'email': 'jean-luc@melenchon.fr',
            'first_name': 'Jean-Luc',
            'last_name': 'Mélenchon'
        })
        response = self.list_view(request)

        # assert it worked
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        new_person = Person.objects.get(email='jean-luc@melenchon.fr')

        self.assertEqual(new_person.first_name, 'Jean-Luc')
        self.assertEqual(new_person.last_name, 'Mélenchon')

    def test_can_modify_current_person(self):
        request = self.factory.patch('', data={
            'first_name': 'Marc'
        })
        response = self.detail_view(request, pk=self.person.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.person.refresh_from_db()
        self.assertEqual(self.person.first_name, 'Marc')

    def test_can_list_persons(self):
        request = self.factory.get('')
        response = self.list_view(request)

        self.assertIn('_items', response.data)
        self.assertIn('_meta', response.data)

        self.assertEqual(len(response.data['_items']), 1)
