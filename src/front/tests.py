from datetime import timedelta
from unittest import mock, skip
from urllib.parse import urlparse

from django.test import TestCase
from django.utils import timezone, formats
from django.http import QueryDict
from rest_framework import status
from django.shortcuts import reverse
from django.contrib.auth import get_user

from lib.tests.mixins import FakeDataMixin
from people.models import Person, PersonTag, PersonForm, PersonFormSubmission
from events.models import Event, RSVP, Calendar, OrganizerConfig, CalendarItem
from groups.models import SupportGroup, Membership
from polls.models import Poll, PollOption, PollChoice

from front.forms import EventForm, SupportGroupForm


from .backend import token_generator


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

    @mock.patch('front.forms.people.geocode_person')
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

    @mock.patch("front.forms.people.send_unsubscribe_email")
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
    @mock.patch("front.forms.people.send_welcome_mail")
    def test_can_post(self, patched_send_welcome_mail):
        response = self.client.post('/inscription/', {'email': 'example@example.com', 'location_zip': '75018'})

        self.assertEqual(response.status_code, 302)
        person = Person.objects.get_by_natural_key('example@example.com')

        patched_send_welcome_mail.delay.assert_called_once()
        self.assertEqual(patched_send_welcome_mail.delay.call_args[0][0], person.pk)


class OverseasSubscriptionTestCase(TestCase):
    @mock.patch("front.forms.people.send_welcome_mail")
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


class NavbarTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_person('test@test.com')

        self.group = SupportGroup.objects.create(
            name="group",
        )
        Membership.objects.create(
            person=self.person,
            supportgroup=self.group,
            is_referent=True,
            is_manager=True
        )

    def test_navbar_authenticated(self):
        self.client.force_login(self.person.role)
        response = self.client.get('/groupes/' + str(self.group.id) + '/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(b'Tableau de bord', response.content)

    def test_navbar_unauthenticated(self):
        response = self.client.get('/groupes/' + str(self.group.id) + '/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(b'Mes groupes', response.content)
        self.assertIn(b'Connexion', response.content)


class PagesLoadingTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_person('test@test.com')
        self.client.force_login(self.person.role)

        now = timezone.now()
        day = timezone.timedelta(days=1)
        hour = timezone.timedelta(hours=1)

        self.event = Event.objects.create(
            name="event",
            start_time=now + day,
            end_time=now + day + hour,
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

    @mock.patch('front.views.dashboard.geocode_person')
    def test_see_event_list(self, geocode_person):
        response = self.client.get('/evenements/')
        self.assertRedirects(response, reverse('dashboard'))
        geocode_person.delay.assert_called_once()

    @mock.patch('front.views.dashboard.geocode_person')
    def test_see_group_list(self, geocode_person):
        response = self.client.get('/groupes/')
        self.assertRedirects(response, reverse('dashboard'))
        geocode_person.delay.assert_called_once()

    def test_see_event_details(self):
        response = self.client.get('/evenements/' + str(self.event.id) + '/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_see_group_details(self):
        response = self.client.get('/groupes/' + str(self.group.id) + '/')
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

        self.event = Event.objects.create(
            name="event",
            start_time=now + day,
            end_time=now + day + hour,
        )

        self.group = SupportGroup.objects.create(
            name="group",
        )

    def test_redirect_when_unauth(self):
        for url in ['/', '/evenements/creer/', '/groupes/creer/',
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


class EventPagesTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_person('test@test.com')
        self.other_person = Person.objects.create_person('other@test.fr')
        self.group = SupportGroup.objects.create(name='Group name')
        Membership.objects.create(supportgroup=self.group, person=self.person, is_manager=True)

        self.now = now = timezone.now().astimezone(timezone.get_default_timezone())
        day = timezone.timedelta(days=1)
        hour = timezone.timedelta(hours=1)

        self.organized_event = Event.objects.create(
            name="Organized event",
            start_time=now + day,
            end_time=now + day + 4 * hour,
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
        )

        RSVP.objects.create(
            person=self.person,
            event=self.rsvped_event,
        )

        self.other_event = Event.objects.create(
            name="Other event",
            start_time=now + 3 * day,
            end_time=now + 3 * day + 4 * hour,
        )

        self.other_rsvp1 = RSVP.objects.create(
            person=self.other_person,
            event=self.rsvped_event
        )

        self.other_rsvp2 = RSVP.objects.create(
            person=self.other_person,
            event=self.other_event
        )

    @mock.patch.object(EventForm, "geocoding_task")
    @mock.patch("front.forms.events.send_event_changed_notification")
    def test_can_modify_organized_event(self, patched_send_notification, patched_geocode):
        self.client.force_login(self.person.role)
        response = self.client.get(reverse('edit_event', kwargs={'pk': self.organized_event.pk}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(
            reverse('edit_event', kwargs={'pk': self.organized_event.pk}),
            data={
                'name': 'New Name',
                'start_time': formats.localize_input(self.now + timezone.timedelta(hours=2), "%d/%m/%Y %H:%M"),
                'end_time': formats.localize_input(self.now + timezone.timedelta(hours=4), "%d/%m/%Y %H:%M"),
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
                'as_group': self.group.pk,
            }
        )

        # the form redirects to the event manage page on success
        self.assertRedirects(response, reverse('manage_event', kwargs={'pk': self.organized_event.pk}))

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

        patched_geocode.delay.assert_called_once()
        args = patched_geocode.delay.call_args[0]

        self.assertEqual(args[0], self.organized_event.pk)
        self.assertIn(self.group, self.organized_event.organizers_groups.all())

    def test_cannot_modify_rsvp_event(self):
        self.client.force_login(self.person.role)

        # manage_page
        response = self.client.get(reverse('manage_event', kwargs={'pk': self.rsvped_event.pk}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # get edit page
        response = self.client.get(reverse('edit_event', kwargs={'pk': self.rsvped_event.pk}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # post edit page
        response = self.client.post(reverse('edit_event', kwargs={'pk': self.rsvped_event.pk}), data={
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
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # add organizer
        response = self.client.post(reverse('manage_event', kwargs={'pk': self.rsvped_event.pk}), data={
            'organizer': str(self.other_rsvp1.pk)
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_modify_other_event(self):
        self.client.force_login(self.person.role)

        # manage_page
        response = self.client.get(reverse('manage_event', kwargs={'pk': self.other_event.pk}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # get edit page
        response = self.client.get(reverse('edit_event', kwargs={'pk': self.other_event.pk}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # post edit page
        response = self.client.post(reverse('edit_event', kwargs={'pk': self.other_event.pk}), data={
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
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # add organizer
        response = self.client.post(reverse('manage_event', kwargs={'pk': self.other_event.pk}), data={
            'organizer': str(self.other_rsvp2.pk)
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @mock.patch('front.views.events.send_rsvp_notification')
    def test_can_rsvp(self, rsvp_notification):
        url = reverse('view_event', kwargs={'pk': self.other_event.pk})
        self.client.force_login(self.person.role)
        response = self.client.get(url)
        self.assertIn('Participer à cet événement', response.content.decode())

        response = self.client.post(url, data={
            'action': 'rsvp'
        }, follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.person, self.other_event.attendees.all())
        self.assertIn('Annuler ma participation', response.content.decode())

        rsvp_notification.delay.assert_called_once()

        rsvp = RSVP.objects.get(person=self.person, event=self.other_event)
        self.assertEqual(rsvp_notification.delay.call_args[0][0], rsvp.pk)

    @skip('REDO')
    @mock.patch("front.forms.events.geocode_event")
    @mock.patch("front.forms.events.send_event_creation_notification")
    def test_can_create_new_event(self, patched_send_event_creation_notification, patched_geocode_event):
        self.client.force_login(self.person.role)

        # get create page, it should contain the name of the group the user manage
        response = self.client.get(reverse('create_event'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'Group name')

        # post create page
        response = self.client.post(reverse('create_event'), data={
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
            'as_group': self.group.pk,
        })
        self.assertRedirects(response, reverse('manage_event', args=[Event.objects.last().pk]))

        try:
            organizer_config = self.person.organizer_configs.exclude(event=self.organized_event).get()
        except (OrganizerConfig.DoesNotExist, OrganizerConfig.MultipleObjectsReturned):
            self.fail('Should have created one organizer config')

        patched_send_event_creation_notification.delay.assert_called_once()
        self.assertEqual(patched_send_event_creation_notification.delay.call_args[0], (organizer_config.pk,))

        patched_geocode_event.delay.assert_called_once()
        self.assertEqual(patched_geocode_event.delay.call_args[0], (organizer_config.event.pk,))

        event = Event.objects.latest(field_name='created')
        self.assertEqual(event.name, 'New Name')
        self.assertIn(self.group, event.organizers_groups.all())


class GroupPageTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_person('test@test.com')
        self.other_person = Person.objects.create_person('other@test.fr')

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

        # other memberships
        Membership.objects.create(
            person=self.other_person,
            supportgroup=self.member_group
        )


        now = timezone.now()
        day = timezone.timedelta(days=1)
        hour = timezone.timedelta(hours=1)
        self.event = Event.objects.create(
            name='événement test pour groupe',
            nb_path='/pseudo/test',
            start_time=now + 3 * day,
            end_time=now + 3 * day + 4 * hour,
        )

        OrganizerConfig.objects.create(
            event=self.event,
            person=self.person,
            as_group=self.referent_group
        )

        self.client.force_login(self.person.role)

    @mock.patch.object(SupportGroupForm, 'geocoding_task')
    @mock.patch("front.forms.groups.send_support_group_changed_notification")
    def test_can_modify_managed_group(self, patched_send_notification, patched_geocode):
        response = self.client.get(reverse('edit_group', kwargs={'pk': self.manager_group.pk}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(
            reverse('edit_group', kwargs={'pk': self.manager_group.pk}),
            data={
                'name': 'Manager',
                'type': 'L',
                'subtypes': ['groupe local'],
                'contact_name': 'Arthur',
                'contact_email': 'a@fhezfe.fr',
                'contact_phone': '06 06 06 06 06',
                'location_name': 'location',
                'location_address1': 'somewhere',
                'location_city': 'Outside',
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
        self.assertCountEqual(args[1], ['contact', 'location'])

        patched_geocode.delay.assert_called_once()
        args = patched_geocode.delay.call_args[0]

        self.assertEqual(args[0], self.manager_group.pk)

    @mock.patch("front.forms.groups.geocode_support_group")
    def test_do_not_geocode_if_address_did_not_change(self, patched_geocode):
        response = self.client.post(
            reverse('edit_group', kwargs={'pk': self.manager_group.pk}),
            data={
                'name': "Manager",
                'type': 'L',
                'subtypes': ['groupe local'],
                'location_name': 'location',
                'location_address1': 'somewhere',
                'location_city': 'Over',
                'location_country': 'DE',
                'contact_name': 'Arthur',
                'contact_email': 'a@fhezfe.fr',
                'contact_phone': '06 06 06 06 06',
            }
        )

        self.assertRedirects(response, reverse('manage_group', kwargs={'pk': self.manager_group.pk}))
        patched_geocode.delay.assert_not_called()

    def test_cannot_modify_member_group(self):
        response = self.client.get(reverse('edit_group', kwargs={'pk': self.member_group.pk}))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @mock.patch('front.views.dashboard.geocode_person')
    def test_can_quit_group(self, geocode_person):
        response = self.client.get(reverse('quit_group', kwargs={'pk': self.member_group.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(reverse('quit_group', kwargs={'pk': self.member_group.pk}))
        self.assertRedirects(response, reverse('dashboard'))
        geocode_person.delay.assert_called_once()

        self.assertFalse(self.member_group.memberships.filter(person=self.person).exists())

    @mock.patch('front.views.groups.send_someone_joined_notification')
    def test_can_join(self, someone_joined):
        url = reverse('view_group', kwargs={'pk': self.manager_group.pk})
        self.client.force_login(self.other_person.role)
        response = self.client.get(url)
        self.assertNotIn(self.other_person, self.manager_group.members.all())
        self.assertIn('Rejoindre ce groupe', response.content.decode())

        response = self.client.post(url, data={
            'action': 'join'
        }, follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.other_person, self.manager_group.members.all())
        self.assertIn('Quitter le groupe', response.content.decode())

        someone_joined.delay.assert_called_once()
        membership = Membership.objects.get(person=self.other_person, supportgroup=self.manager_group)
        self.assertEqual(someone_joined.delay.call_args[0][0], membership.pk)

    @mock.patch.object(SupportGroupForm, 'geocoding_task')
    @mock.patch('front.forms.groups.send_support_group_creation_notification')
    def test_can_create_group(self, patched_send_support_group_creation_notification, patched_geocode_support_group):
        self.client.force_login(self.person.role)

        # get create page
        response = self.client.get(reverse('create_group'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(reverse('perform_create_group'), data={
            'name': 'New name',
            'type': 'L',
            'subtypes': ['groupe local'],
            'contact_email': 'a@fhezfe.fr',
            'contact_phone': '+33606060606',
            'contact_hide_phone': 'on',
            'location_name': 'location',
            'location_address1': 'somewhere',
            'location_city': 'Over',
            'location_country': 'DE',
            'notify': 'on',
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        try:
            membership = self.person.memberships.filter(is_referent=True).exclude(
                supportgroup=self.referent_group).get()
        except (Membership.DoesNotExist, Membership.MultipleObjectsReturned):
            self.fail('Should have created one membership')

        patched_send_support_group_creation_notification.delay.assert_called_once()
        self.assertEqual(patched_send_support_group_creation_notification.delay.call_args[0], (membership.pk,))

        patched_geocode_support_group.delay.assert_called_once()
        self.assertEqual(patched_geocode_support_group.delay.call_args[0], (membership.supportgroup.pk,))

        group = SupportGroup.objects.first()
        self.assertEqual(group.name, 'New name')
        self.assertEqual(group.subtypes.all().count(), 1)

    @mock.patch('front.views.dashboard.geocode_person')
    def test_cannot_view_unpublished_group(self, geocode_person):
        self.client.force_login(self.person.role)

        self.referent_group.published = False
        self.referent_group.save()

        res = self.client.get(reverse('dashboard'))
        self.assertNotContains(res, self.referent_group.pk)
        geocode_person.delay.assert_called_once()

        res = self.client.get('/groupes/{}/'.format(self.referent_group.pk))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

        group_pages = ['view_group', 'manage_group', 'edit_group', 'change_group_location', 'quit_group']
        for page in group_pages:
            res = self.client.get(reverse(page, args=(self.referent_group.pk,)))
            self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND, '"{}" did not return 404'.format(page))

    def test_can_see_groups_events(self):
        response = self.client.get(reverse('view_group', args=[self.referent_group.pk]))

        self.assertContains(response, "événement test pour groupe")


class NBUrlsTestCase(TestCase):
    def setUp(self):
        now = timezone.now()
        day = timezone.timedelta(days=1)
        hour = timezone.timedelta(hours=1)
        self.event = Event.objects.create(
            name='Test',
            nb_path='/pseudo/test',
            start_time=now + 3 * day,
            end_time=now + 3 * day + 4 * hour,
        )

        self.group = SupportGroup.objects.create(
            name='Test',
            nb_path='/12/grouptest'
        )

    def test_event_url_redirect(self):
        response = self.client.get('/old/pseudo/test')

        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.url, reverse('view_event', kwargs={'pk': self.event.id}))

    def test_group_url_redirect(self):
        response = self.client.get('/old/12/grouptest')

        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.url, reverse('view_group', kwargs={'pk': self.group.id}))

    def test_create_group_redirect(self):
        # new event page
        response = self.client.get('/old/users/event_pages/new?parent_id=103')

        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.url, reverse('create_event'))

    def test_unkown_gives_404(self):
        response = self.client.get('/old/nimp')

        self.assertEqual(response.status_code, 404)


class AuthenticationTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_person('test@test.com', )

        from django.contrib.auth import load_backend
        self.soft_backend = 'front.backend.MailLinkBackend'

    def test_can_connect_with_query_params(self):
        p = self.person.pk
        code = token_generator.make_token(self.person)

        response = self.client.get(reverse('volunteer'), data={'p': p, 'code': code})

        self.assertRedirects(response, reverse('volunteer'))
        self.assertEqual(get_user(self.client), self.person.role)

    def test_can_access_soft_login_while_already_connected(self):
        self.client.force_login(self.person.role, self.soft_backend)

        response = self.client.get(reverse('volunteer'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cannot_access_hard_login_page_while_soft_logged_in(self):
        self.client.force_login(self.person.role, self.soft_backend)

        response = self.client.get(reverse('create_group'))

        self.assertRedirects(
            response, reverse('oauth_redirect_view') + '?next=' + reverse('create_group'),
            target_status_code=status.HTTP_302_FOUND
        )

    def test_unsubscribe_redirects_to_message_preferences_when_logged(self):
        message_preferences_path = reverse('message_preferences')
        unsubscribe_path = reverse('unsubscribe')

        self.client.force_login(self.person.role)
        response = self.client.get(unsubscribe_path)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        target_url = urlparse(response.url)
        self.assertEqual(target_url.path, message_preferences_path)


class CalendarPageTestCase(TestCase):
    def setUp(self):
        self.calendar = Calendar.objects.create(
            name="My calendar",
            slug="my_calendar",
        )

        now = timezone.now()
        day = timezone.timedelta(days=1)
        hour = timezone.timedelta(hours=1)

        for i in range(20):
            e = Event.objects.create(
                name="Event {}".format(i),
                calendar=self.calendar,
                start_time=now + i * day,
                end_time=now + i * day + hour
            )
            CalendarItem.objects.create(event=e, calendar=self.calendar)

    def can_view_page(self):
        # can show first page
        res = self.client.get('/agenda/my_calendar/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # there's a next button
        self.assertContains(res, '<li class="next">')
        self.assertContains(res, 'href="?page=2"')

        # there's no previous button
        self.assertNotContains(res, '<li class="previous">')

        # can display second page
        res = self.client.get('/agenda/my_calendar/?page=2')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # there's a next button
        self.assertNotContains(res, '<li class="next">')

        # there's no previous button
        self.assertContains(res, '<li class="previous">')
        self.assertContains(res, 'href="?page=1"')


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
        self.complex_form.end_time = timezone.now() - timedelta(days=1)
        self.complex_form.save()

        res = self.client.get('/formulaires/formulaire-complexe/')
        self.assertContains(res, "Ce formulaire est maintenant fermé.")

    def test_cannot_post_on_closed_forms(self):
        self.complex_form.end_time = timezone.now() - timedelta(days=1)
        self.complex_form.save()

        res = self.client.post('/formulaires/formulaire-complexe/', data={
            'tag': 'tag2',
            'contact_phone': '06 34 56 78 90',
            'custom-field': 'Mon super champ texte libre',
            'custom-person-field': 'Mon super champ texte libre à mettre dans Person.metas'
        })
        self.assertContains(res, "Ce formulaire est maintenant fermé.")


class PollTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create(
            email='participant@example.com',
            created=timezone.now() + timedelta(days=-10)
        )
        self.poll = Poll.objects.create(
            title='title',
            description='description',
            start=timezone.now() + timedelta(hours=-1),
            end=timezone.now() + timedelta(days=1),
            rules={
                'min_options': 2,
                'max_options': 2,
            }
        )
        self.poll.tags.add(PersonTag.objects.create(label="test_tag"))
        self.poll1 = PollOption.objects.create(poll=self.poll, description='Premier')
        self.poll2 = PollOption.objects.create(poll=self.poll, description='Deuxième')
        self.poll3 = PollOption.objects.create(poll=self.poll, description='Troisième')
        self.client.force_login(self.person.role)

    def test_can_view_poll(self):
        res = self.client.get(reverse('participate_poll', args=[self.poll.pk]))

        self.assertContains(res, '<h2 class="headline">title</h2>')
        self.assertContains(res, '<p>description</p>')
        self.assertContains(res, 'Premier')
        self.assertContains(res, 'Deuxième')
        self.assertContains(res, 'Troisième')

    def test_cannot_view_not_started_poll(self):
        self.poll.start = timezone.now() + timedelta(hours=1)
        self.poll.save()
        res = self.client.get(reverse('participate_poll', args=[self.poll.pk]))

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_view_finished_poll(self):
        self.poll.start = timezone.now() + timedelta(days=-1, hours=-1)
        self.poll.end = timezone.now() + timedelta(hours=-1)
        self.poll.save()
        res = self.client.get(reverse('participate_poll', args=[self.poll.pk]))

        self.assertRedirects(res, reverse('finished_poll'))

    def test_can_participate(self):
        res = self.client.post(reverse('participate_poll', args=[self.poll.pk]),data={
            'choice': [str(self.poll1.pk), str(self.poll3.pk)]
        })

        self.assertRedirects(res, reverse('participate_poll', args=[self.poll.pk]))
        choice = PollChoice.objects.first()
        self.assertIn('test_tag', [str(tag) for tag in self.person.tags.all()])
        self.assertEqual(choice.person, self.person)
        self.assertCountEqual(choice.selection, [str(self.poll1.pk), str(self.poll3.pk)])

    def test_cannot_participate_if_just_registered(self):
        person = Person.objects.create(email='just_created@example.com')
        self.client.force_login(person.role)

        res = self.client.post(reverse('participate_poll', args=[self.poll.pk]), data={
            'choice': [str(self.poll1.pk), str(self.poll3.pk)]
        })
        self.assertContains(res, 'trop récemment', status_code=403)


    def test_cannot_participate_twice(self):
        self.client.post(reverse('participate_poll', args=[self.poll.pk]), data={
            'choice': [str(self.poll1.pk), str(self.poll3.pk)]
        })

        res = self.client.get(reverse('participate_poll', args=[self.poll.pk]))
        self.assertContains(res, 'Vous avez déjà participé')

        res = self.client.post(reverse('participate_poll', args=[self.poll.pk]), data={
            'choice': [str(self.poll1.pk), str(self.poll3.pk)]
        })

        self.assertContains(res, 'déjà participé', status_code=403)

    def test_must_respect_choice_number(self):
        res = self.client.post(reverse('participate_poll', args=[self.poll.pk]), data={
            'choice': [str(self.poll1.pk)]
        })
        self.assertContains(res, 'minimum')

        res = self.client.post(reverse('participate_poll', args=[self.poll.pk]), data={
            'choice': [str(self.poll1.pk),str(self.poll2.pk),str(self.poll3.pk)]
        })
        self.assertContains(res, 'maximum')


class DashboardTestCase(FakeDataMixin, TestCase):
    @mock.patch('front.views.dashboard.geocode_person')
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
