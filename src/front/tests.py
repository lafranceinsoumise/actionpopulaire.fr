from unittest import mock

from django.test import TestCase
from django.utils import timezone, formats
from django.http import QueryDict
from rest_framework import status
from django.shortcuts import reverse
import django_countries

from people.models import Person
from events.models import Event, RSVP, Calendar, OrganizerConfig
from groups.models import SupportGroup, Membership


class SimpleSubscriptionFormTestCase(TestCase):
    def test_can_post(self):
        response = self.client.post('/inscription/', {'email': 'example@example.com', 'location_zip': '75018'})

        self.assertEqual(response.status_code, 302)
        Person.objects.get_by_natural_key('example@example.com')


class OverseasSubscriptionForm(TestCase):
    def test_can_post(self):
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


class PagesLoadingTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_person('test@test.com')
        self.client.force_login(self.person.role)

        now = timezone.now()
        day = timezone.timedelta(days=1)
        hour = timezone.timedelta(hours=1)

        calendar = Calendar.objects.create(label='default')

        self.event = Event.objects.create(
            name="event",
            start_time=now + day,
            end_time=now + day + hour,
            calendar=calendar
        )

        OrganizerConfig.objects.create(
            event=self.event,
            person=self.person,
            is_creator=True
        )

        self.group = SupportGroup.objects.create(
            name="group",
        )
        Membership.objects.create(
            person=self.person,
            supportgroup=self.group,
            is_referent=True,
            is_manager=True
        )

    def test_see_event_list(self):
        response = self.client.get('/evenements/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_see_group_list(self):
        response = self.client.get('/groupes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_see_create_event(self):
        response = self.client.get('/evenements/creer/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_see_create_group(self):
        response = self.client.get('/groupes/creer/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_see_update_event(self):
        response = self.client.get('/evenements/%s/modifier/' % self.event.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_see_update_group(self):
        response = self.client.get('/groupes/%s/modifier/' % self.group.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AuthorizationTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_person('test@test.com')

        now = timezone.now()
        day = timezone.timedelta(days=1)
        hour = timezone.timedelta(hours=1)

        calendar = Calendar.objects.create(label='default')

        self.event = Event.objects.create(
            name="event",
            start_time=now + day,
            end_time=now + day + hour,
            calendar=calendar
        )

        self.group = SupportGroup.objects.create(
            name="group",
        )

    def test_redirect_when_unauth(self):
        for url in ['/evenements/', '/groupes/', '/evenements/creer/', '/groupes/creer/',
                    '/evenements/%s/modifier/' % self.event.pk, '/groupes/%s/modifier/' % self.group.pk]:
            response = self.client.get(url)
            query = QueryDict(mutable=True)
            query['next'] = url
            self.assertRedirects(response, '/authentification/?%s' % query.urlencode(safe='/'), target_status_code=302)

    def test_403_when_editing_event(self):
        self.client.force_login(self.person.role)

        response = self.client.get('/evenements/%s/modifier/' % self.event.pk)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.post('/evenements/%s/modifier/' % self.event.pk)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_403_when_editing_group(self):
        self.client.force_login(self.person.role)

        response = self.client.get('/groupes/%s/modifier/' % self.group.pk)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.post('/groupes/%s/modifier/' % self.group.pk)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_oauth_backend(self):
        from .backend import OAuth2Backend
        backend = OAuth2Backend()
        profile_url = reverse('legacy:person-detail', kwargs={'pk': self.person.pk})

        self.assertEqual(self.person.role, backend.authenticate(profile_url=profile_url))


class EventPageTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_person('test@test.com')

        now = timezone.now()
        day = timezone.timedelta(days=1)
        hour = timezone.timedelta(hours=1)

        calendar = Calendar.objects.create(label='default')

        self.organized_event = Event.objects.create(
            name="Organized event",
            start_time=now + day,
            end_time=now + day + 4 * hour,
            calendar=calendar
        )

        OrganizerConfig.objects.create(
            event=self.organized_event,
            person=self.person,
            is_creator=True
        )

        self.rsvped_event = Event.objects.create(
            name="RSVPed event",
            start_time=now + 2 * day,
            end_time=now + 2 * day + 2 * hour,
            calendar=calendar
        )
        RSVP.objects.create(
            person=self.person,
            event=self.rsvped_event,
        )

        self.other_event = Event.objects.create(
            name="Other event",
            start_time=now + 3 * day,
            end_time=now + 3 * day + 4 * hour,
            calendar=calendar
        )

    @mock.patch("front.views.events.send_event_changed_notification")
    def test_can_modify_organized_event(self, patched_send_notification):
        self.client.force_login(self.person.role)
        response = self.client.get(reverse('edit_event', kwargs={'pk': self.organized_event.pk}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(
            reverse('edit_event', kwargs={'pk': self.organized_event.pk}),
            data={
                'name': 'New Name',
                'start_time': formats.localize_input(timezone.now() + timezone.timedelta(hours=2), "%d/%m/%Y %H:%M"),
                'end_time': formats.localize_input(timezone.now() + timezone.timedelta(hours=4), "%d/%m/%Y %H:%M"),
                'contact_name': 'Arthur',
                'contact_email': 'a@ziefzji.fr',
                'contact_phone': '06 06 06 06 06',
                'location_name': 'somewhere',
                'location_address1': 'over',
                'location_zip': 'the',
                'location_city': 'rainbow',
                'location_country': 'FR',
                'description': 'New description',
                'notify': 'on',
            }
        )

        # the form redirects to the event list on success
        self.assertRedirects(response, reverse('list_events'))

        # accessing the messages: see https://stackoverflow.com/a/14909727/1122474
        messages = list(response.wsgi_request._messages)

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].level_tag, 'success')

        # send_support_group_changed_notification.delay should have been called once, with the pk of the group as
        # first argument, and the changes as the second
        patched_send_notification.delay.assert_called_once()
        args = patched_send_notification.delay.call_args[0]

        self.assertEqual(args[0], self.organized_event.pk)
        self.assertCountEqual(args[1], ['contact', 'location', 'timing', 'information'])

    def test_cannot_modify_rsvp_event(self):
        self.client.force_login(self.person.role)
        response = self.client.get(reverse('edit_event', kwargs={'pk': self.rsvped_event.pk}))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_modify_other_event(self):
        self.client.force_login(self.person.role)
        response = self.client.get(reverse('edit_event', kwargs={'pk': self.other_event.pk}))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class GroupPageTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_person('test@test.com')

        self.referent_group = SupportGroup.objects.create(
            name="Referent",
        )
        Membership.objects.create(
            person=self.person,
            supportgroup=self.referent_group,
            is_referent=True
        )

        self.manager_group = SupportGroup.objects.create(
            name="Manager",
            location_name='location',
            location_address1='somewhere',
            location_city='Over',
            location_country='DE'
        )

        Membership.objects.create(
            person=self.person,
            supportgroup=self.manager_group,
            is_referent=False,
            is_manager=True
        )

        self.member_group = SupportGroup.objects.create(
            name="Member"
        )
        Membership.objects.create(
            person=self.person,
            supportgroup=self.member_group
        )

        self.client.force_login(self.person.role)

    @mock.patch("front.views.groups.send_support_group_changed_notification")
    def test_can_modify_managed_group(self, patched_send_notification):
        response = self.client.get(reverse('edit_group', kwargs={'pk': self.manager_group.pk}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(
            reverse('edit_group', kwargs={'pk': self.manager_group.pk}),
            data={
                'name': 'New name',
                'contact_name': 'Arthur',
                'contact_email': 'a@fhezfe.fr',
                'contact_phone': '06 06 06 06 06',
                'location_name': 'location',
                'location_address1': 'somewhere',
                'location_city': 'Over',
                'location_country': 'DE',
                'notify': 'on',
            }
        )

        self.assertRedirects(response, reverse('manage_group', kwargs={'pk': self.manager_group.pk}))

        # accessing the messages: see https://stackoverflow.com/a/14909727/1122474
        messages = list(response.wsgi_request._messages)

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].level_tag, 'success')

        # send_support_group_changed_notification.delay should have been called once, with the pk of the group as
        # first argument, and the changes as the second
        patched_send_notification.delay.assert_called_once()
        args = patched_send_notification.delay.call_args[0]

        self.assertEqual(args[0], self.manager_group.pk)
        self.assertCountEqual(args[1], ['contact', 'information'])

    def test_cannot_modify_member_group(self):
        response = self.client.get(reverse('edit_group', kwargs={'pk': self.member_group.pk}))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
