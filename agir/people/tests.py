from unittest import mock

from django.test import TestCase, override_settings
from django.contrib.auth import authenticate
from django.utils import timezone
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core import mail
from redislite import StrictRedis

from rest_framework.test import APIRequestFactory, force_authenticate, APITestCase
from rest_framework import status
from rest_framework.reverse import reverse

from agir.authentication.models import Role
from .models import Person, PersonTag, PersonEmail, PersonForm, PersonFormSubmission
from .viewsets import LegacyPersonViewSet
from . import tasks

from agir.events.models import Event, RSVP
from agir.groups.models import SupportGroup, Membership

from agir.lib.tests.mixins import FakeDataMixin


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
    @mock.patch('agir.people.tasks.update_mailtrain')
    def test_person_is_updated_in_mailtrain(self, update_mailtrain):
        person = Person.objects.create_person('test1@domain.com')

        update_mailtrain.delay.assert_called_once()
        args = update_mailtrain.delay.call_args[0]
        self.assertEqual(args[0], person.pk)

    @override_settings(MAILTRAIN_DISABLE=False)
    @mock.patch('agir.people.tasks.update_mailtrain')
    def test_person_is_updated_when_email_deleted(self, update_mailtrain):
        person = Person.objects.create_person('test1@domain.com')
        p2 = PersonEmail.objects.create(address='test2@domain.com', person=person)

        update_mailtrain.reset_mock()

        p2.delete()

        update_mailtrain.delay.assert_called_once()
        self.assertEqual(update_mailtrain.delay.call_args[0][0], person.pk)


class LegacyPersonEndpointTestCase(APITestCase):
    def as_viewer(self, request):
        force_authenticate(request, self.viewer_person.role)

    def setUp(self):
        self.basic_person = Person.objects.create_person(
            email='jean.georges@domain.com',
            first_name='Jean',
            last_name='Georges',
        )

        self.viewer_person = Person.objects.create_person(
            email='viewer@viewer.fr'
        )

        self.adder_person = Person.objects.create_person(
            email='adder@adder.fr',
        )

        self.changer_person = Person.objects.create_person(
            email='changer@changer.fr'
        )

        person_content_type = ContentType.objects.get_for_model(Person)
        view_permission = Permission.objects.get(content_type=person_content_type, codename='view_person')
        add_permission = Permission.objects.get(content_type=person_content_type, codename='add_person')
        change_permission = Permission.objects.get(content_type=person_content_type, codename='change_person')

        self.viewer_person.role.user_permissions.add(view_permission)
        self.adder_person.role.user_permissions.add(add_permission)
        self.changer_person.role.user_permissions.add(view_permission, change_permission)

        self.event = Event.objects.create(
            name='event',
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(hours=2)
        )

        self.rsvp = RSVP.objects.create(
            person=self.basic_person,
            event=self.event
        )

        self.supportgroup = SupportGroup.objects.create(
            name='Group',
        )

        self.membership = Membership.objects.create(
            person=self.basic_person,
            supportgroup=self.supportgroup
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

        self.redis_instance = StrictRedis()
        self.redis_patcher = mock.patch('agir.lib.token_bucket.get_redis_client')
        mock_get_auth_redis_client = self.redis_patcher.start()
        mock_get_auth_redis_client.return_value = self.redis_instance

    def test_cannot_list_while_unauthenticated(self):
        request = self.factory.get('')
        response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_can_only_view_self_while_unprivileged(self):
        request = self.factory.get('')
        force_authenticate(request, self.basic_person.role)
        response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['_items']), 1)
        self.assertEqual(response.data['_items'][0]['_id'], str(self.basic_person.pk))

    def test_can_see_self_while_authenticated(self):
        self.client.force_authenticate(self.basic_person.role)
        response = self.client.get('/legacy/people/me/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['_id'], str(self.basic_person.pk))

    def test_cannot_see_self_while_unauthenticated(self):
        response = self.client.get('/legacy/people/me/')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_view_details_while_unauthenticated(self):
        request = self.factory.get('')
        response = self.detail_view(request, pk=self.basic_person.pk)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_can_see_self_while_unprivileged(self):
        request = self.factory.get('')
        force_authenticate(request, self.basic_person.role)
        response = self.detail_view(request, pk=self.basic_person.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cannot_view_others_details_while_unprivileged(self):
        request = self.factory.get('')
        force_authenticate(request, self.basic_person.role)
        response = self.detail_view(request, pk=self.viewer_person.pk)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_contain_simple_fields(self):
        request = self.factory.get('')
        self.as_viewer(request)
        response = self.detail_view(request, pk=self.basic_person.pk)

        expected_fields = {'_id', 'id', 'email', 'first_name', 'last_name', 'bounced', 'bounced_date'}

        assert expected_fields.issubset(set(response.data))

    def test_contains_only_whitelisted_fields_while_unprivileged(self):
        self.client.force_authenticate(self.basic_person.role)
        response = self.client.get('/legacy/people/me/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(('url', '_id', 'email', 'first_name', 'last_name', 'email_opt_in',
        'events', 'groups', 'location'), response.data.keys())

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
        force_authenticate(request, self.adder_person.role)
        response = self.list_view(request)

        # assert it worked
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        new_person = Person.objects.get(email='jean-luc@melenchon.fr')

        self.assertEqual(new_person.first_name, 'Jean-Luc')
        self.assertEqual(new_person.last_name, 'Mélenchon')

    @mock.patch("agir.people.viewsets.send_welcome_mail")
    def test_can_subscribe_new_person(self, patched_send_welcome_mail):
        self.client.force_login(self.adder_person.role)
        response = self.client.post(reverse('legacy:person-subscribe-list'), data={
            'email': 'guillaume@email.com',
        })

        self.assertEqual(response.status_code, 403)

        response = self.client.post(reverse('legacy:person-subscribe-list'), data={
            'email': 'guillaume@email.com',
        }, ** {'HTTP_X_WORDPRESS_CLIENT': '192.168.0.1'})

        new_person = Person.objects.get(email='guillaume@email.com')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['p'], new_person.id)
        self.assertIsNotNone(response.data['code'])
        patched_send_welcome_mail.delay.assert_called_once()
        self.assertEqual(patched_send_welcome_mail.delay.call_args[0], (new_person.id,))

    def test_cannot_post_new_person_with_existing_email(self):
        request = self.factory.post('', data={
            'email': self.basic_person.email
        })
        force_authenticate(request, self.adder_person.role)
        response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    @override_settings(MAILTRAIN_DISABLE=False)
    @mock.patch('agir.people.tasks.update_mailtrain')
    def test_can_update_email_list(self, update_mailtrain):
        """
        We test at the same time that we can replace the list,
        and that we can set the primary email with the 'email' field
        """
        request = self.factory.patch('', data={
            'emails': [
                {
                    'address': 'test@example.com',
                    'bounced': True
                },
                {
                    'address': 'testprimary@example.com',
                    'bounced': False
                },
                {
                    'address': 'jean.georges@domain.com'
                }
            ],
            'email': 'testprimary@example.com'
        })
        force_authenticate(request, self.changer_person.role)
        response = self.detail_view(request, pk=self.basic_person.pk)

        update_mailtrain.delay.assert_called_once()
        args = update_mailtrain.delay.call_args[0]
        self.assertEqual(args[0], self.basic_person.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.basic_person.email, 'testprimary@example.com')
        self.assertEqual(self.basic_person.emails.all()[2].address, 'test@example.com')
        self.assertEqual(self.basic_person.emails.all()[2].bounced, True)

    def test_can_update_bounced_status(self):
        request = self.factory.patch('', data={
            'bounced': True
        })
        force_authenticate(request, self.changer_person.role)
        response = self.detail_view(request, pk=self.basic_person.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.basic_person.emails.all()[0].address, 'jean.georges@domain.com')
        self.assertEqual(self.basic_person.emails.all()[0].bounced, True)
        self.assertLess(self.basic_person.emails.all()[0].bounced_date, timezone.now())

    def test_cannot_modify_while_unauthenticated(self):
        request = self.factory.patch('', data={
            'first_name': 'Marc'
        })
        response = self.detail_view(request, pk=self.basic_person.pk)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_can_modify_self(self):
        request = self.factory.patch('', data={
            'email': 'marcus@cool.md',
            'first_name': 'Marc'
        })
        force_authenticate(request, self.basic_person.role)
        response = self.detail_view(request, pk=self.basic_person.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.basic_person.refresh_from_db()
        self.assertEqual(self.basic_person.first_name, 'Marc')
        self.assertTrue(self.basic_person.emails.filter(address='marcus@cool.md').exists())

    def test_can_modify_with_global_perm(self):
        request = self.factory.patch('', data={
            'first_name': 'Marc'
        })
        force_authenticate(request, self.changer_person.role)
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
        self.as_viewer(request)
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

    def test_can_see_groups(self):
        request = self.factory.get('')
        self.as_viewer(request)
        response = self.detail_view(request, pk=self.basic_person.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('groups', response.data)

        self.assertCountEqual(response.data['groups'], [self.supportgroup.pk])

    def test_can_post_users_with_empty_null_and_blank_fields(self):
        request = self.factory.post('', data={
            'email': "putain@demerde.com",
            'location_address1': '',
            'location_address2': None,
            'country_code': None
        })
        force_authenticate(request, self.adder_person.role)

        response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class LegacyEndpointFieldsTestCase(TestCase):
    def get_request(self, path='', data=None, **extra):
        return self.as_superuser(self.factory.get(path, data, **extra))

    def patch_request(self, path='', data=None, **extra):
        return self.as_superuser(self.factory.patch(path, data, **extra))

    def as_superuser(self, request):
        force_authenticate(request, self.superuser.role)
        return request

    def setUp(self):
        self.superuser = Person.objects.create_superperson('super@user.fr', None)

        self.tag = PersonTag.objects.create(label='tag1')

        self.person1 = Person.objects.create_person('person1@domain.fr')
        self.person2 = Person.objects.create(email='person2@domain.fr', nb_id=12345)
        self.person3 = Person.objects.create(email='person3@domain.fr', nb_id=67890)

        self.detail_view = LegacyPersonViewSet.as_view({
            'get': 'retrieve',
            'put': 'update',
            'patch': 'partial_update',
            'delete': 'destroy'
        })

        self.list_view = LegacyPersonViewSet.as_view({
            'get': 'list',
            'post': 'create',
        })

        self.factory = APIRequestFactory()

    def test_can_add_existing_tag(self):
        request = self.patch_request(data={'tags': ['tag1']})

        response = self.detail_view(request, pk=self.person1.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.person1.refresh_from_db()

        self.assertCountEqual(self.person1.tags.all(), [self.tag])

    def test_can_add_new_tag(self):
        request = self.patch_request(data={'tags': ['tag2']})

        response = self.detail_view(request, pk=self.person1.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        qs = PersonTag.objects.filter(label='tag2')
        self.person1.refresh_from_db()
        self.assertEqual(len(qs), 1)
        self.assertCountEqual(qs, self.person1.tags.all())

    def test_can_update_location_fields(self):
        request = self.patch_request(data={
            'location': {
                'address': '40 boulevard Auguste Blanqui, 75013 Paris, France',
                'address1': '40 boulevard Auguste Blanqui',
                'city': 'Paris',
                'country_code': 'FR',
                'zip': '75013',
            }
        })

        response = self.detail_view(request, pk=self.person1.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.person1.refresh_from_db()

        self.assertEqual(self.person1.location_address, '40 boulevard Auguste Blanqui, 75013 Paris, France')
        self.assertEqual(self.person1.location_address1, '40 boulevard Auguste Blanqui')
        self.assertEqual(self.person1.location_city, 'Paris')
        self.assertEqual(self.person1.location_country.code, 'FR')
        self.assertEqual(self.person1.location_zip, '75013')


class LegacyEndpointLookupFilterTestCase(TestCase):
    def get_request(self, path='', data=None, **extra):
        return self.as_superuser(self.factory.get(path, data, **extra))

    def as_superuser(self, request):
        force_authenticate(request, self.superuser.role)
        return request

    def setUp(self):
        self.superuser = Person.objects.create_superperson('super@user.fr', None)
        self.person1 = Person.objects.create_person('person1@domain.fr')
        self.person2 = Person.objects.create(email='person2@domain.fr', nb_id=12345)
        self.person3 = Person.objects.create(email='person3@domain.fr', nb_id=67890)

        self.detail_view = LegacyPersonViewSet.as_view({
            'get': 'retrieve',
            'put': 'update',
            'patch': 'partial_update',
            'delete': 'destroy'
        })

        self.list_view = LegacyPersonViewSet.as_view({
            'get': 'list',
            'post': 'create',
        })

        self.factory = APIRequestFactory()

    def test_can_query_by_pk(self):
        request = self.get_request()

        response = self.detail_view(request, pk=self.person1.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.person1.email)

    def test_can_query_by_nb_id(self):
        request = self.get_request()

        response = self.detail_view(request, pk=str(self.person2.nb_id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.person2.email)

    def test_can_filter_by_email(self):
        request = self.get_request(data={'email': 'person1@domain.fr'})
        response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['_items']), 1)


class PeopleTasksTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_person('me@me.org')

    def test_welcome_mail(self):
        tasks.send_welcome_mail(self.person.pk)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].recipients(), [self.person.email])

    def test_unsubscribe_mail(self):
        tasks.send_unsubscribe_email(self.person.pk)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].recipients(), [self.person.email])


class DashboardTestCase(FakeDataMixin, TestCase):
    @mock.patch('agir.people.views.geocode_person')
    def test_contains_everything(self, geocode_person):
        self.client.force_login(self.data['people']['user2'].role)
        response = self.client.get(reverse('dashboard'))

        geocode_person.delay.assert_called_once()
        self.assertEqual(geocode_person.delay.call_args[0], (self.data['people']['user2'].pk, ))

        # own email
        self.assertContains(response, 'user2@example.com')
        # managed group
        self.assertContains(response, self.data['groups']['user2_group'].name)
        # member groups
        self.assertContains(response, self.data['groups']['user1_group'].name)
        # next events
        self.assertContains(response, self.data['events']['user1_event1'].name)
        # events of group
        self.assertContains(response, self.data['events']['user1_event2'].name)


class MessagePreferencesTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_person('test@test.com')
        self.person.add_email('test2@test.com')
        self.client.force_login(self.person.role)

    def test_can_load_message_preferences_page(self):
        res = self.client.get('/message_preferences/')

        # should show the current email address
        self.assertContains(res, 'test@test.com')
        self.assertContains(res, 'test2@test.com')

    def test_can_see_email_management(self):
        res = self.client.get('/message_preferences/adresses/')

        # should show the current email address
        self.assertContains(res, 'test@test.com')
        self.assertContains(res, 'test2@test.com')

    def test_can_add_delete_address(self):
        emails = list(self.person.emails.all())

        # should be possible to get the delete page for one of the two addresses, and to actually delete
        res = self.client.get('/message_preferences/adresses/{}/supprimer/'.format(emails[1].pk))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res = self.client.post('/message_preferences/adresses/{}/supprimer/'.format(emails[1].pk))
        self.assertRedirects(res, reverse('email_management'))

        # address should indeed be gone
        self.assertEqual(len(self.person.emails.all()), 1)
        self.assertEqual(self.person.emails.first(), emails[0])

        # both get and post should give 403 when there is only one primary address
        res = self.client.get('/message_preferences/adresses/{}/supprimer/'.format(emails[0].pk))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        res = self.client.post('/message_preferences/adresses/{}/supprimer/'.format(emails[0].pk))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_can_add_address(self):
        res = self.client.post('/message_preferences/adresses/', data={'address': 'test3@test.com'})
        self.assertRedirects(res, '/message_preferences/adresses/')

        res = self.client.post('/message_preferences/adresses/', data={'address': 'TeST4@TeSt.COM'})
        self.assertRedirects(res, '/message_preferences/adresses/')

        self.assertCountEqual(
            [e.address for e in self.person.emails.all()],
            ['test@test.com', 'test2@test.com', 'test3@test.com', 'test4@test.com']
        )

    def test_can_stop_messages(self):
        res = self.client.post('/message_preferences/', data={
            'no_mail': True,
            'gender': '',
            'primary_email': self.person.emails.first().id
        })
        self.assertEqual(res.status_code, 302)
        self.person.refresh_from_db()
        self.assertEqual(self.person.subscribed, False)
        self.assertEqual(self.person.event_notifications, False)
        self.assertEqual(self.person.group_notifications, False)
        self.assertEqual(self.person.draw_participation, False)


class ProfileFormTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_person(
            'test@test.com'
        )

    def test_can_add_tag(self):
        self.client.force_login(self.person.role)
        response = self.client.post(reverse('change_profile'), {'info blogueur': 'on'})

        self.assertEqual(response.status_code, 302)
        self.assertIn('info blogueur', [tag.label for tag in self.person.tags.all()])

    @mock.patch('agir.people.forms.geocode_person')
    def test_can_change_address(self, geocode_person):
        self.client.force_login(self.person.role)

        address_fields = {
            'location_address1': '73 boulevard Arago',
            'location_zip': '75013',
            'location_country': 'FR',
            'location_city': 'Paris',
        }

        response = self.client.post(reverse('change_profile'), address_fields)

        geocode_person.delay.assert_called_once()
        self.assertEqual(geocode_person.delay.call_args[0], (self.person.pk,))

        geocode_person.reset_mock()
        response = self.client.post(reverse('change_profile'), {
            'first_name': 'Arthur',
            'last_name': 'Cheysson',
            **address_fields
        })
        geocode_person.delay.assert_not_called()


class UnsubscribeFormTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_person('test@test.com')

    @mock.patch("agir.people.forms.send_unsubscribe_email")
    def test_can_post(self, patched_send_unsubscribe_email):
        response = self.client.post(reverse('unsubscribe'), {'email': 'test@test.com'})

        self.person.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.person.subscribed, False)
        self.assertEqual(self.person.event_notifications, False)
        self.assertEqual(self.person.group_notifications, False)
        patched_send_unsubscribe_email.delay.assert_called_once()
        self.assertEqual(patched_send_unsubscribe_email.delay.call_args[0], (self.person.pk,))


class DeleteFormTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_person('delete@delete.com')

    def test_can_delete_account(self):
        self.client.force_login(self.person.role)

        response = self.client.post(reverse('delete_account'))
        self.assertEqual(response.status_code, 302)
        with self.assertRaises(Person.DoesNotExist):
            Person.objects.get(pk=self.person.pk)


class SimpleSubscriptionFormTestCase(TestCase):
    @mock.patch("agir.people.forms.send_welcome_mail")
    def test_can_post(self, patched_send_welcome_mail):
        response = self.client.post('/inscription/', {'email': 'example@example.com', 'location_zip': '75018'})

        self.assertEqual(response.status_code, 302)
        person = Person.objects.get_by_natural_key('example@example.com')

        patched_send_welcome_mail.delay.assert_called_once()
        self.assertEqual(patched_send_welcome_mail.delay.call_args[0][0], person.pk)


class OverseasSubscriptionTestCase(TestCase):
    @mock.patch("agir.people.forms.send_welcome_mail")
    def test_can_post(self, patched_send_welcome_mail):
        response = self.client.post('/inscription/etranger/', {
            'email': 'example@example.com',
            'location_address1': '1 ZolaStraße',
            'location_zip': '10178',
            'location_city': 'Berlin',
            'location_country': 'DE'
        })

        self.assertEqual(response.status_code, 302)
        person = Person.objects.get_by_natural_key('example@example.com')
        self.assertEqual(person.location_city, 'Berlin')

        patched_send_welcome_mail.delay.assert_called_once()
        self.assertEqual(patched_send_welcome_mail.delay.call_args[0][0], person.pk)


class PersonFormTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_person('person@corp.com')
        self.person.meta['custom-person-field'] = 'Valeur méta préexistante'
        self.person.save()
        self.tag1 = PersonTag.objects.create(label='tag1', description='Description TAG1')
        self.tag2 = PersonTag.objects.create(label='tag2', description='Description TAG2')

        self.single_tag_form = PersonForm.objects.create(
            title='Formulaire simple',
            slug='formulaire-simple',
            description='Ma description simple',
            confirmation_note='Ma note de fin',
            main_question='QUESTION PRINCIPALE',
            custom_fields=[{
                'title': 'Profil',
                'fields': [{
                    'id': 'contact_phone',
                    'person_field': True
                }]
            }],
        )
        self.single_tag_form.tags.add(self.tag1)

        self.complex_form = PersonForm.objects.create(
            title='Formulaire complexe',
            slug='formulaire-complexe',
            description='Ma description complexe',
            confirmation_note='Ma note de fin',
            main_question='QUESTION PRINCIPALE',
            custom_fields=[{
                'title': 'Détails',
                'fields': [
                    {
                        'id': 'custom-field',
                        'type': 'short_text',
                        'label': 'Mon label'
                    },
                    {
                        'id': 'custom-person-field',
                        'type': 'short_text',
                        'label': 'Prout',
                        'person_field': True
                    },
                    {
                        'id': 'contact_phone',
                        'person_field': True
                    }
                ]
            }]
        )
        self.complex_form.tags.add(self.tag1)
        self.complex_form.tags.add(self.tag2)

        self.client.force_login(self.person.role)

    def test_flatten_fields_property(self):
        self.assertEqual(self.complex_form.fields_dict, {
             'custom-field': {
                 'id': 'custom-field',
                 'type': 'short_text',
                 'label': 'Mon label'
             },
             'custom-person-field': {
                 'id': 'custom-person-field',
                 'type': 'short_text',
                 'label': 'Prout',
                 'person_field': True
             },
             'contact_phone': {
                 'id': 'contact_phone',
                 'person_field': True
             }
        })

    def test_title_and_description(self):
        res = self.client.get('/formulaires/formulaire-simple/')

        # Contient le titre et la description
        self.assertContains(res, self.single_tag_form.title)
        self.assertContains(res, self.single_tag_form.description)

        res = self.client.get('/formulaires/formulaire-simple/confirmation/')
        self.assertContains(res, self.single_tag_form.title)
        self.assertContains(res, self.single_tag_form.confirmation_note)

    def test_can_validate_simple_form(self):
        res = self.client.get('/formulaires/formulaire-simple/')

        # contains phone number field
        self.assertContains(res, 'contact_phone')

        # check contact phone is compulsory
        res = self.client.post('/formulaires/formulaire-simple/', data={})
        self.assertContains(res, 'has-error')

        # check can validate
        res = self.client.post('/formulaires/formulaire-simple/', data={'contact_phone': '06 04 03 02 04'})
        self.assertRedirects(res, '/formulaires/formulaire-simple/confirmation/')

        # check user has been well modified
        self.person.refresh_from_db()

        self.assertEqual(self.person.contact_phone, '+33604030204')
        self.assertIn(self.tag1, self.person.tags.all())

        submissions = PersonFormSubmission.objects.all()
        self.assertEqual(len(submissions), 1)
        self.assertEqual(submissions[0].data['contact_phone'], '+33604030204')

    def test_can_validate_complex_form(self):
        res = self.client.get('/formulaires/formulaire-complexe/')

        self.assertContains(res, 'contact_phone')
        self.assertContains(res, 'custom-field')
        self.assertContains(res, 'Valeur méta préexistante')

        # assert tag is compulsory
        res = self.client.post('/formulaires/formulaire-complexe/', data={
            'contact_phone': '06 34 56 78 90',
            'custom-field': 'Mon super champ texte libre'
        })
        self.assertContains(res, 'has-error')

        res = self.client.post('/formulaires/formulaire-complexe/', data={
            'tag': 'tag2',
            'contact_phone': '06 34 56 78 90',
            'custom-field': 'Mon super champ texte libre',
            'custom-person-field': 'Mon super champ texte libre à mettre dans Person.metas'
        })
        self.assertRedirects(res, '/formulaires/formulaire-complexe/confirmation/')

        self.person.refresh_from_db()

        self.assertCountEqual(self.person.tags.all(), [self.tag2])
        self.assertEqual(self.person.meta['custom-person-field'], 'Mon super champ texte libre à mettre dans Person.metas')

        submissions = PersonFormSubmission.objects.all()
        self.assertEqual(len(submissions), 1)

        self.assertEqual(submissions[0].data['custom-field'], 'Mon super champ texte libre')
        self.assertEqual(submissions[0].data['custom-person-field'], 'Mon super champ texte libre à mettre dans Person.metas')

    def test_cannot_view_closed_forms(self):
        self.complex_form.end_time = timezone.now() - timezone.timedelta(days=1)
        self.complex_form.save()

        res = self.client.get('/formulaires/formulaire-complexe/')
        self.assertContains(res, "Ce formulaire est maintenant fermé.")

    def test_cannot_post_on_closed_forms(self):
        self.complex_form.end_time = timezone.now() - timezone.timedelta(days=1)
        self.complex_form.save()

        res = self.client.post('/formulaires/formulaire-complexe/', data={
            'tag': 'tag2',
            'contact_phone': '06 34 56 78 90',
            'custom-field': 'Mon super champ texte libre',
            'custom-person-field': 'Mon super champ texte libre à mettre dans Person.metas'
        })
        self.assertContains(res, "Ce formulaire est maintenant fermé.")
