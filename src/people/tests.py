from django.test import TestCase
from django.contrib.auth import authenticate
from django.utils import timezone
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status
from rest_framework.reverse import reverse

from .models import Person
from .viewsets import LegacyPersonViewSet

from events.models import Event, RSVP, Calendar


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
    def as_viewer(self, request):
        force_authenticate(request, self.viewer_person)

    def setUp(self):
        self.basic_person = Person.objects.create(
            email='jean.georges@domain.com',
            first_name='Jean',
            last_name='Georges',
        )

        self.viewer_person = Person.objects.create(
            email='viewer@viewer.fr'
        )

        self.adder_person = Person.objects.create(
            email='adder@adder.fr',
        )

        self.changer_person = Person.objects.create(
            email='changer@changer.fr'
        )

        person_content_type = ContentType.objects.get_for_model(Person)
        view_permission = Permission.objects.get(content_type=person_content_type, codename='view_person')
        add_permission = Permission.objects.get(content_type=person_content_type, codename='add_person')
        change_permission = Permission.objects.get(content_type=person_content_type, codename='change_person')

        self.viewer_person.user_permissions.add(view_permission)
        self.adder_person.user_permissions.add(add_permission)
        self.changer_person.user_permissions.add(change_permission)

        calendar = Calendar.objects.create(label='calendar')

        self.event = Event.objects.create(
            name='event',
            calendar=calendar,
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(hours=2)
        )

        self.rsvp = RSVP.objects.create(
            person=self.basic_person,
            event=self.event
        )

        self.factory = APIRequestFactory()

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

    def test_cannot_list_while_unauthenticated(self):
        request = self.factory.get('')
        response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_view_while_unprivileged(self):
        request = self.factory.get('')
        force_authenticate(request, self.basic_person)
        response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_view_details_while_unauthenticated(self):
        request = self.factory.get('')
        response = self.detail_view(request, pk=self.basic_person.pk)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_view_details_while_unprivileged(self):
        request = self.factory.get('')
        force_authenticate(request, self.basic_person)
        response = self.detail_view(request, pk=self.viewer_person.pk)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_contain_simple_fields(self):
        request = self.factory.get('')
        self.as_viewer(request)
        response = self.detail_view(request, pk=self.basic_person.pk)

        expected_fields = {'_id', 'id', 'email', 'first_name', 'last_name', 'bounced', 'bounced_date'}

        assert expected_fields.issubset(set(response.data))

    def test_return_correct_values(self):
        request = self.factory.get('')
        self.as_viewer(request)
        response = self.detail_view(request, pk=self.basic_person.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.basic_person.email, response.data['email'])
        self.assertEqual(self.basic_person.first_name, response.data['first_name'])
        self.assertEqual(self.basic_person.last_name, response.data['last_name'])

    def test_cannot_post_new_person_while_unauthenticated(self):
        request = self.factory.post('', data={
            'email': 'jean-luc@melenchon.fr',
            'first_name': 'Jean-Luc',
            'last_name': 'Mélenchon'
        })
        response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_can_post_new_person(self):
        request = self.factory.post('', data={
            'email': 'jean-luc@melenchon.fr',
            'first_name': 'Jean-Luc',
            'last_name': 'Mélenchon'
        })
        force_authenticate(request, self.adder_person)
        response = self.list_view(request)

        # assert it worked
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        new_person = Person.objects.get(email='jean-luc@melenchon.fr')

        self.assertEqual(new_person.first_name, 'Jean-Luc')
        self.assertEqual(new_person.last_name, 'Mélenchon')

    def test_cannot_modify_while_unauthenticated(self):
        request = self.factory.patch('', data={
            'first_name': 'Marc'
        })
        response = self.detail_view(request, pk=self.basic_person.pk)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_can_modify_current_person(self):
        request = self.factory.patch('', data={
            'first_name': 'Marc'
        })
        force_authenticate(request, self.changer_person)
        response = self.detail_view(request, pk=self.basic_person.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.basic_person.refresh_from_db()
        self.assertEqual(self.basic_person.first_name, 'Marc')

    def test_can_list_persons(self):
        request = self.factory.get('')
        self.as_viewer(request)
        response = self.list_view(request)

        self.assertIn('_items', response.data)
        self.assertIn('_meta', response.data)

        self.assertEqual(len(response.data['_items']), 4)
        self.assertCountEqual(
            [person['email'] for person in response.data['_items']],
            ['jean.georges@domain.com', 'adder@adder.fr', 'changer@changer.fr', 'viewer@viewer.fr']
        )

    def test_can_see_events(self):
        request = self.factory.get('')
        force_authenticate(request, self.viewer_person)
        response = self.detail_view(request, pk=self.basic_person.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('events', response.data)

        self.assertCountEqual(response.data['events'], [self.event.pk])

    def test_can_see_rsvps(self):
        request = self.factory.get('')
        self.as_viewer(request)
        response = self.detail_view(request, pk=self.basic_person.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('rsvps', response.data)

        self.assertCountEqual(response.data['rsvps'],
                              [reverse('legacy:rsvp-detail', kwargs={'pk': self.rsvp.pk}, request=request)])
