from unittest import skip, mock

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone, formats

from rest_framework.reverse import reverse
from rest_framework import status

from agir.groups.models import SupportGroup, Membership
from agir.payments.models import Payment
from agir.people.models import Person, PersonForm, PersonFormSubmission

from ..forms import EventForm
from ..models import Event, Calendar, RSVP, OrganizerConfig, CalendarItem
from ..views import notification_listener as event_notification_listener


class OrganizerAsGroupTestCase(TestCase):
    def setUp(self):
        self.start_time = timezone.now()
        self.end_time = self.start_time + timezone.timedelta(hours=2)
        self.calendar = Calendar.objects.create_calendar('calendar', user_contributed=True)
        self.person = Person.objects.create(email='test@example.com')
        self.event = Event.objects.create(
            name='Event test',
            start_time=self.start_time,
            end_time=self.end_time
        )
        self.group1 = SupportGroup.objects.create(
            name='Nom'
        )
        Membership.objects.create(person=self.person, supportgroup=self.group1, is_manager=True)
        self.group2 = SupportGroup.objects.create(
            name='Nom'
        )
        Membership.objects.create(person=self.person, supportgroup=self.group2)

        self.organizer_config = OrganizerConfig(person=self.person, event=self.event, is_creator=True)

    def test_can_add_group_as_organizer(self):
        self.organizer_config.as_group = self.group1
        self.organizer_config.full_clean()

    def test_cannot_add_group_as_organizer_if_not_manager(self):
        self.organizer_config.as_group = self.group2
        with self.assertRaises(ValidationError):
            self.organizer_config.full_clean()


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
            allow_guests=True
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
    @mock.patch("agir.events.forms.send_event_changed_notification")
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

    @mock.patch('agir.events.views.send_rsvp_notification')
    def test_can_rsvp(self, rsvp_notification):
        url = reverse('view_event', kwargs={'pk': self.other_event.pk})
        self.client.force_login(self.person.role)
        response = self.client.get(url)
        self.assertIn('Participer à cet événement', response.content.decode())

        response = self.client.post(reverse('rsvp_event', kwargs={'pk': self.other_event.pk}), follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.person, self.other_event.attendees.all())
        self.assertEqual(2, self.other_event.participants)
        self.assertIn('Annuler ma participation', response.content.decode())

        rsvp_notification.delay.assert_called_once()

        rsvp = RSVP.objects.get(person=self.person, event=self.other_event)
        self.assertEqual(rsvp_notification.delay.call_args[0][0], rsvp.pk)

    @mock.patch('agir.events.views.send_rsvp_notification')
    def test_can_update_rsvp(self, rsvp_notification):
        url = reverse('view_event', kwargs={'pk': self.rsvped_event.pk})
        self.client.force_login(self.person.role)
        response = self.client.get(url)
        self.assertIn('Inscription validée', response.content.decode())
        self.assertEqual(2, self.rsvped_event.participants)

        response = self.client.post(reverse('rsvp_event', kwargs={'pk': self.rsvped_event.pk}),
                                    data={'guests':1}, follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.person, self.rsvped_event.attendees.all())
        self.assertEqual(3, self.rsvped_event.participants)
        self.assertIn('Inscription validée (2 participant⋅e⋅s)', response.content.decode())

        rsvp_notification.delay.assert_called_once()

        rsvp = RSVP.objects.get(person=self.person, event=self.rsvped_event)
        self.assertEqual(rsvp_notification.delay.call_args[0][0], rsvp.pk)

    @mock.patch('agir.events.views.send_rsvp_notification')
    def test_cannot_rsvp_add_guests_if_not_allowed(self, rsvp_notification):
        url = reverse('view_event', kwargs={'pk': self.other_event.pk})
        self.client.force_login(self.person.role)
        response = self.client.get(url)
        self.assertIn('Participer à cet événement', response.content.decode())

        response = self.client.post(reverse('rsvp_event', kwargs={'pk': self.other_event.pk}),
                                    data={'guests': 1}, follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.person, self.other_event.attendees.all())
        self.assertEqual(2, self.other_event.participants)
        self.assertIn('Inscription validée', response.content.decode())

    def test_cannot_rsvp_if_max_participants_reached(self):
        self.other_event.max_participants = 1
        self.other_event.save()

        url = reverse('view_event', kwargs={'pk': self.other_event.pk})
        self.client.force_login(self.person.role)
        response = self.client.get(url)
        self.assertNotIn('Participer à cet événement', response.content.decode())

        response = self.client.post(reverse('rsvp_event', kwargs={'pk': self.other_event.pk}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("capacité maximum", response.content.decode())

        self.assertEqual(1, self.other_event.participants)

    @skip('REDO')
    @mock.patch("agir.front.forms.events.geocode_event")
    @mock.patch("agir.front.forms.events.send_event_creation_notification")
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

    @mock.patch('agir.events.views.send_rsvp_notification')
    def test_rsvp_and_add_guests_subscription_form_event(self, rsvp_notification):
        self.client.force_login(self.person.role)
        self.other_event.subscription_form = PersonForm.objects.create(
            title='Formulaire événement',
            slug='formulaire-evenement',
            description='Ma description complexe',
            confirmation_note='Ma note de fin',
            main_question='QUESTION PRINCIPALE',
            custom_fields=[{
                'title': 'Détails',
                'fields': [
                    {
                        'id': 'custom-field',
                        'type': 'short_text',
                        'label': 'Mon label',
                        'person_field': True
                    }
                ]
            }]
        )
        self.other_event.save()

        response = self.client.post(reverse('rsvp_event', kwargs={'pk': self.other_event.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(reverse('rsvp_event', kwargs={'pk': self.other_event.pk}), data={'custom-field':'prout'}, follow=True)

        self.person.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.person, self.other_event.attendees.all())
        self.assertEqual(self.person.meta['custom-field'], 'prout')
        self.assertEqual(2, self.other_event.participants)
        self.assertIn('Inscription validée', response.content.decode())

        ## Inscription d'un⋅e deuxième participant⋅e : échec sans allow_guests
        response = self.client.get(reverse('rsvp_event', kwargs={'pk': self.other_event.pk}))
        self.assertNotContains(response, "Inscrire un⋅e autre participant⋅e")
        response = self.client.post(reverse('rsvp_event', kwargs={'pk': self.other_event.pk}),
                                    data={'custom-field': 'prout-prout'}, follow=True)
        self.assertContains(response, "ne permet pas")
        self.assertEqual(2, self.other_event.participants)

        ## Inscription d'un⋅e deuxième participant⋅e : succès
        self.other_event.allow_guests = True
        self.other_event.save()

        response = self.client.get(reverse('rsvp_event', kwargs={'pk': self.other_event.pk}))
        self.assertContains(response, "Inscrire un⋅e autre participant⋅e")
        response = self.client.post(reverse('rsvp_event', kwargs={'pk': self.other_event.pk}),
                                    data={'custom-field': 'prout-prout'}, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.person, self.other_event.attendees.all())
        self.assertEqual(3, self.other_event.participants)
        rsvp = RSVP.objects.get(person=self.person, event=self.other_event)
        self.person.refresh_from_db()
        self.assertEqual(self.person.meta['custom-field'], 'prout')
        self.assertEqual(rsvp.guests_form_submissions.first().data['custom-field'], 'prout-prout')
        self.assertIn('Inscription validée (2 participant⋅e⋅s)', response.content.decode())

    @mock.patch('agir.events.views.send_rsvp_notification')
    def test_rsvp_paid_event_and_add_guests(self, rsvp_notification):
        self.client.force_login(self.person.role)
        self.other_event.subscription_form = PersonForm.objects.create(
            title='Formulaire événement',
            slug='formulaire-evenement',
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
                    }
                ]
            }]
        )
        self.other_event.payment_parameters = {"price": 1000}
        self.other_event.save()

        response = self.client.post(reverse('rsvp_event', kwargs={'pk': self.other_event.pk}),
                                    data={'custom-field': 'prout'}, follow=True)

        self.assertRedirects(response, reverse('pay_event'))

        res = self.client.get(reverse('pay_event'))
        self.assertEqual(res.status_code, 200)

        res = self.client.post(reverse('pay_event'), data={
            'submission': PersonFormSubmission.objects.last().pk,
            'event': str(self.other_event.pk),
            'first_name': 'Marc',
            'last_name': 'Frank',
            'location_address1': '4 rue de Chaume',
            'location_address2': '',
            'location_zip': '33000',
            'location_city': 'Bordeaux',
            'location_country': 'FR',
            'contact_phone': '06 45 78 98 45'
        })

        # no other payment
        payment = Payment.objects.get()

        self.assertRedirects(res, reverse('payment_redirect', args=(payment.pk,)))

        # fake systempay webhook
        payment.status = Payment.STATUS_COMPLETED
        payment.save()
        event_notification_listener(payment)

        self.assertIn(self.person, self.other_event.attendees.all())

        rsvp_notification.delay.assert_called_once()

        rsvp = RSVP.objects.get(person=self.person, event=self.other_event)
        self.assertEqual(rsvp_notification.delay.call_args[0][0], rsvp.pk)

        # test ajout invité alors que allow_guests = False
        response = self.client.post(reverse('rsvp_event', kwargs={'pk': self.other_event.pk}),
                                    data={'custom-field': 'prout'}, follow=True)

        self.assertRedirects(response, reverse('view_event', kwargs={'pk': self.other_event.pk}))
        self.assertContains(response, "ne permet pas")

        # test ajout invité
        self.other_event.allow_guests = True
        self.other_event.save()

        response = self.client.post(reverse('rsvp_event', kwargs={'pk': self.other_event.pk}),
                                    data={'custom-field': 'prout'}, follow=True)

        self.assertRedirects(response, reverse('pay_event'))

        res = self.client.get(reverse('pay_event'))
        self.assertEqual(res.status_code, 200)

        res = self.client.post(reverse('pay_event'), data={
            'submission': PersonFormSubmission.objects.last().pk,
            'event': str(self.other_event.pk),
            'first_name': 'Marcy',
            'last_name': 'Franky',
            'location_address1': '4 rue de Chaume',
            'location_address2': '',
            'location_zip': '33000',
            'location_city': 'Bordeaux',
            'location_country': 'FR',
            'contact_phone': '06 45 78 98 45'
        })

        payment = Payment.objects.last()

        self.assertRedirects(res, reverse('payment_redirect', args=(payment.pk,)))

        payment.status = Payment.STATUS_COMPLETED
        payment.save()
        event_notification_listener(payment)


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
