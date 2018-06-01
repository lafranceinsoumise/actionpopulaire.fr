import json
from unittest import skip, mock

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.db import IntegrityError, transaction
from django.utils import timezone, formats
from django.utils.http import urlquote_plus
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geos import Point
from django.core import mail

from rest_framework.test import APIRequestFactory, force_authenticate, APITestCase
from rest_framework.reverse import reverse
from rest_framework import status

from . import tasks
from .forms import EventForm
from .models import Event, Calendar, RSVP, OrganizerConfig, CalendarItem
from .views import notification_listener as event_notification_listener
from ..lib.utils import front_url
from ..groups.models import SupportGroup, Membership
from ..payments.models import Payment
from ..people.models import Person, PersonForm, PersonFormSubmission
from ..clients.models import Client
from .viewsets import LegacyEventViewSet, RSVPViewSet


class BasicEventTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.calendar = Calendar.objects.create_calendar('test')

        cls.start_time = timezone.now()
        cls.end_time = cls.start_time + timezone.timedelta(hours=2)

    def test_can_create_event(self):
        event = Event.objects.create(
            name='Event test',
            start_time=self.start_time,
            end_time=self.end_time
        )

        self.assertEqual(event, Event.objects.get(name='Event test'))

    def test_cannot_create_without_dates(self):
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Event.objects.create(
                    name='Event test',
                    start_time=self.start_time
                )

        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Event.objects.create(
                    name='Event test 2',
                    end_time=self.end_time
                )


class RSVPTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(hours=3)

        cls.event = Event.objects.create(
            name='Test',
            start_time=start_time,
            end_time=end_time
        )

        cls.person = Person.objects.create(
            email='marc.machin@truc.com'
        )

    def test_create_rsvps(self):
        rsvp = RSVP.objects.create(
            person=self.person,
            event=self.event
        )

        self.assertCountEqual([rsvp], self.person.rsvps.all())
        self.assertCountEqual([rsvp], self.event.rsvps.all())
        self.assertCountEqual([self.person], self.event.attendees.all())

    def test_cannot_create_without_person(self):
        with self.assertRaises(IntegrityError):
            RSVP.objects.create(
                event=self.event
            )

    def test_cannot_create_without_event(self):
        with self.assertRaises(IntegrityError):
            RSVP.objects.create(
                person=self.person
            )

    def test_unique_rsvp(self):
        RSVP.objects.create(
            person=self.person,
            event=self.event
        )

        with self.assertRaises(IntegrityError):
            RSVP.objects.create(
                person=self.person,
                event=self.event
            )

    def test_participants_count(self):
        RSVP.objects.create(
            person=self.person,
            event=self.event,
            guests=10
        )

        self.assertEqual(self.event.participants, 11)

        RSVP.objects.create(
            person=Person.objects.create(email='person2@domain.com'),
            event=self.event,
        )

        self.assertEqual(self.event.participants, 12)


class LegacyEventViewSetTestCase(TestCase):
    def setUp(self):
        self.event = Event.objects.create(
            name='event',
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(hours=4),
            nb_id=1
        )

        self.unprivileged_person = Person.objects.create_person(
            email='jean.georges@domain.com',
            first_name='Jean',
            last_name='Georges',
        )

        self.changer_person = Person.objects.create_person(
            email='changer@changer.fr'
        )

        self.one_event_person = Person.objects.create_person(
            email='event@event.com'
        )

        self.attendee_person = Person.objects.create_person(
            email='attendee@attendee.com'
        )

        self.view_all_person = Person.objects.create_person(
            email='viewer@viewer.fr'
        )

        event_content_type = ContentType.objects.get_for_model(Event)
        change_permission = Permission.objects.get(content_type=event_content_type, codename='change_event')
        view_hidden_permission = Permission.objects.get(content_type=event_content_type, codename='view_hidden_event')

        self.changer_person.role.user_permissions.add(change_permission)
        self.view_all_person.role.user_permissions.add(view_hidden_permission)

        OrganizerConfig.objects.create(
            event=self.event,
            person=self.one_event_person,
            is_creator=True
        )

        RSVP.objects.create(
            person=self.attendee_person,
            event=self.event,
            guests=10
        )

        self.detail_view = LegacyEventViewSet.as_view({
            'get': 'retrieve',
            'put': 'update',
            'patch': 'partial_update',
            'delete': 'destroy'
        })

        self.list_view = LegacyEventViewSet.as_view({
            'get': 'list',
            'post': 'create'
        })

        self.new_event_data = {
            'name': 'event 2',
            'start_time': timezone.now().isoformat(),
            'end_time': (timezone.now() + timezone.timedelta(hours=2)).isoformat(),
        }

        self.factory = APIRequestFactory()

    def test_can_list_event_while_unauthenticated(self):
        request = self.factory.get('')
        response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('_items', response.data)
        self.assertEqual(len(response.data['_items']), 1)

        item = response.data['_items'][0]

        self.assertEqual(item['_id'], str(self.event.pk))
        self.assertEqual(item['name'], self.event.name)
        self.assertEqual(item['participants'], self.event.participants)
        assert {'name', 'path', 'id', 'location', 'contact', 'tags', 'coordinates', 'participants'}.issubset(item)

    def unpublish_event(self):
        self.event.published = False
        self.event.save()

    def test_cannot_list_unpublished_events_while_unauthicated(self):
        self.unpublish_event()
        request = self.factory.get('')
        response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('_items', response.data)
        self.assertEqual(len(response.data['_items']), 0)

    def test_can_see_event_details_while_unauthenticated(self):
        request = self.factory.get('')
        response = self.detail_view(request, pk=self.event.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['_id'], str(self.event.pk))

    def test_cannot_view_unpublished_events_while_unauthicated(self):
        self.unpublish_event()
        request = self.factory.get('')
        response = self.detail_view(request, pk=self.event.pk)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_can_view_unpublished_groups_with_correct_permissions(self):
        self.unpublish_event()
        request = self.factory.get('')
        force_authenticate(request, self.view_all_person.role)
        response = self.detail_view(request, pk=self.event.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['_id'], str(self.event.pk))

    def test_cannot_create_event_while_unauthenticated(self):
        request = self.factory.post('', data=self.new_event_data)

        response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_modify_event_while_unauthenticated(self):
        request = self.factory.put('', data=self.new_event_data)

        response = self.detail_view(request, pk=self.event.pk)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_modify_event_without_permission(self):
        request = self.factory.put('', data=self.new_event_data)
        force_authenticate(request, self.unprivileged_person.role)

        response = self.detail_view(request, pk=self.event.pk)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_can_create_event_whith_no_privilege(self):
        request = self.factory.post('', data=self.new_event_data)
        force_authenticate(request, self.unprivileged_person.role)

        response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('_id', response.data)
        new_id = response.data['_id']

        events = Event.objects.all()
        event = Event.objects.get(pk=new_id)

        self.assertEqual(len(events), 2)
        self.assertEqual(event.organizers.first(), self.unprivileged_person)
        self.assertIn(new_id, {str(e.id) for e in events})

    def test_can_modify_event_with_global_perm(self):
        request = self.factory.patch('', data={
            'description': 'Plus mieux!',
            'published': False,
            'organizers': [
                reverse('legacy:person-detail', kwargs={'pk': self.unprivileged_person.pk})
            ]
        })

        force_authenticate(request, user=self.changer_person.role)

        response = self.detail_view(request, pk=self.event.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.event.refresh_from_db()

        self.assertEqual(self.event.description, 'Plus mieux!')
        self.assertEqual(self.event.published, False)
        # When PATCHing through a client, the organizers should be repaced by
        # the new list
        self.assertIn(self.unprivileged_person, self.event.organizers.all())
        self.assertNotIn(self.one_event_person, self.event.organizers.all())

    def test_field_is_organizer(self):
        request = self.factory.get('')
        force_authenticate(request, user=self.one_event_person.role)
        response = self.detail_view(request, pk=self.event.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['is_organizer'], True)

    def test_organizer_can_modify_event(self):
        request = self.factory.patch('', data={
            'description': 'Plus mieux!',
            'organizers': [
                reverse('legacy:person-detail', kwargs={'pk': self.unprivileged_person.pk})
            ]
        })

        force_authenticate(request, user=self.one_event_person.role)

        response = self.detail_view(request, pk=self.event.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.event.refresh_from_db()

        # The organizer should be able to modify list of other organizer but not
        # to remove themselves
        self.assertEqual(self.event.description, 'Plus mieux!')
        self.assertIn(self.unprivileged_person, self.event.organizers.all())
        self.assertIn(self.one_event_person, self.event.organizers.all())

    def test_cannot_create_event_with_same_nb_id(self):
        self.client.force_login(self.unprivileged_person.role)
        response = self.client.post('/legacy/events/', data={
            **self.new_event_data,
            'id': self.event.nb_id
        })

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_can_get_event_summary(self):
        response = self.client.get('/legacy/events/summary/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 1)


class FiltersTestCase(APITestCase):
    def setUp(self):
        self.superuser = Person.objects.create_superperson('super@user.fr', None)

        self.calendar1 = calendar1 = Calendar.objects.create_calendar('Agenda')
        self.calendar2 = calendar2 = Calendar.objects.create_calendar('Agenda2')

        tz = timezone.get_default_timezone()

        self.paris_1_month_event = Event.objects.create(
            name='Paris+1month',
            nb_id=1,
            start_time=timezone.now() + timezone.timedelta(weeks=4),
            end_time=timezone.now() + timezone.timedelta(weeks=4, hours=2),
            coordinates=Point(2.349722, 48.853056),  # ND de Paris
        )
        CalendarItem.objects.create(
            event=self.paris_1_month_event,
            calendar=self.calendar1
        )

        self.amiens_2_months_event = Event.objects.create(
            name='Amiens+2months',
            nb_path='/amiens_july',
            start_time=timezone.now() + timezone.timedelta(weeks=8),
            end_time=timezone.now() + timezone.timedelta(weeks=8, hours=2),
            coordinates=Point(2.301944, 49.8944),  # ND d'Amiens
        )
        CalendarItem.objects.create(
            event=self.amiens_2_months_event,
            calendar=self.calendar1
        )


        self.marseille_3_months_event = Event.objects.create(
            name='Marseille+3months',
            start_time=timezone.now() + timezone.timedelta(weeks=12),
            end_time=timezone.now() + timezone.timedelta(weeks=12, hours=2),
            coordinates=Point(5.36472, 43.30028),  # Saint-Marie-Majeure de Marseille
        )
        CalendarItem.objects.create(
            event=self.marseille_3_months_event,
            calendar=self.calendar2
        )


        self.strasbourg_yesterday = Event.objects.create(
            name="Strasbourg+yesterday",
            start_time=timezone.now() - timezone.timedelta(hours=15),
            end_time=timezone.now() - timezone.timedelta(hours=13),
            coordinates=Point(7.7779, 48.5752),  # ND de Strasbourg
        )
        CalendarItem.objects.create(
            event=self.strasbourg_yesterday,
            calendar=self.calendar2
        )

        self.eiffel_coordinates = [2.294444, 48.858333]

    def test_can_query_by_pk(self):
        response = self.client.get('/legacy/events/%s/' % self.paris_1_month_event.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.paris_1_month_event.name)

    def test_can_query_by_nb_id(self):
        response = self.client.get('/legacy/events/%s/' % self.paris_1_month_event.nb_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['_id'], str(self.paris_1_month_event.pk))

    def test_filter_coordinates_no_results(self):
        # la tour eiffel est à plus d'un kilomètre de Notre-Dame
        filter_string = json.dumps({
            "max_distance": 1000,
            "coordinates": self.eiffel_coordinates,
        })

        response = self.client.get('/legacy/events/?close_to=%s' % filter_string)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('_items', response.data)
        self.assertEqual(len(response.data['_items']), 0)

    def test_filter_coordinates_one_result(self):
        # la tour eiffel est à moins de 10 km de Notre-Dame
        filter_string = json.dumps({
            "max_distance": 10000,
            "coordinates": self.eiffel_coordinates,
        })

        response = self.client.get('/legacy/events/?close_to=%s' % filter_string)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('_items', response.data)
        self.assertEqual(len(response.data['_items']), 1)
        self.assertEqual(response.data['_items'][0]['_id'], str(self.paris_1_month_event.pk))

    def test_filter_by_path(self):
        response = self.client.get('/legacy/events/?path=/amiens_july')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('_items', response.data)
        self.assertEqual(len(response.data['_items']), 1)
        self.assertEqual(response.data['_items'][0]['_id'], str(self.amiens_2_months_event.pk))

    def test_order_by_distance_to(self):
        response = self.client.get('/legacy/events/?order_by_distance_to=%s' % json.dumps(self.eiffel_coordinates))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('_items', response.data)
        self.assertEqual(len(response.data['_items']), 3)
        self.assertEqual(
            [item['_id'] for item in response.data['_items']],
            [str(self.paris_1_month_event.id), str(self.amiens_2_months_event.id),
             str(self.marseille_3_months_event.id)]
        )

    def test_can_directly_retrieve_past_event(self):
        response = self.client.get('/legacy/events/%s/' % self.strasbourg_yesterday.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('_id', response.data)
        self.assertEqual(response.data['_id'], str(self.strasbourg_yesterday.pk))

    def test_can_filter_by_date_after(self):
        # make sure event in progress at the "after" date are included
        response = self.client.get(
            '/legacy/events/?after=%s' %
            urlquote_plus((timezone.now() + timezone.timedelta(weeks=8, hours=1)).isoformat())
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('_items', response.data)
        self.assertCountEqual(
            [item['_id'] for item in response.data['_items']],
            [str(self.amiens_2_months_event.id), str(self.marseille_3_months_event.id)]
        )

    def test_can_filter_by_date_before(self):
        response = self.client.get(
            '/legacy/events/?before=%s' % urlquote_plus(
                (timezone.now() + timezone.timedelta(weeks=4, hours=1)).isoformat())
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('_items', response.data)
        self.assertCountEqual(
            [item['_id'] for item in response.data['_items']],
            [str(self.strasbourg_yesterday.id), str(self.paris_1_month_event.id)]
        )

    def test_can_filter_by_calendar(self):
        response = self.client.get('/legacy/events/?calendar=%s' % self.calendar1.slug)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('_items', response.data)
        self.assertCountEqual(
            [item['_id'] for item in response.data['_items']],
            [str(e.id) for e in Event.objects.filter(calendars=self.calendar1)]
        )


class RSVPEndpointTestCase(TestCase):
    def get_request(self, path='', data=None, **extra):
        return self.factory.get(path, data, **extra)

    def as_privileged(self, request):
        force_authenticate(request, self.privileged_user.role)
        return request

    def as_organizer(self, request):
        force_authenticate(request, self.organizer.role)
        return request

    def as_unprivileged(self, request):
        force_authenticate(request, self.unprivileged_person.role)
        return request

    def setUp(self):
        self.privileged_user = Person.objects.create_superperson('super@user.fr', None)

        self.organizer = Person.objects.create_person(
            email='event@event.com'
        )

        self.unprivileged_person = Person.objects.create_person(
            email='unprivileged@event.com',
        )

        tz = timezone.get_default_timezone()

        self.event = Event.objects.create(
            name='Paris+June',
            nb_id=1,
            start_time=tz.localize(timezone.datetime(2017, 6, 15, 18)),
            end_time=tz.localize(timezone.datetime(2017, 6, 15, 22)),
            coordinates=Point(2.349722, 48.853056),  # ND de Paris
        )

        self.secondary_event = Event.objects.create(
            name='Amiens+July',
            nb_path='/amiens_july',
            start_time=tz.localize(timezone.datetime(2017, 7, 15, 18)),
            end_time=tz.localize(timezone.datetime(2017, 7, 15, 22)),
            coordinates=Point(2.301944, 49.8944),  # ND d'Amiens
        )

        self.unprivileged_rsvp = RSVP.objects.create(
            event=self.event,
            person=self.unprivileged_person,
            guests=0
        )

        self.organizer_rsvp = RSVP.objects.create(
            event=self.event,
            person=self.organizer,
            guests=1,
        )

        self.other_rsvp = RSVP.objects.create(
            event=self.secondary_event,
            person=self.unprivileged_person
        )

        rsvp_content_type = ContentType.objects.get_for_model(RSVP)
        add_permission = Permission.objects.get(content_type=rsvp_content_type, codename='add_rsvp')
        change_permission = Permission.objects.get(content_type=rsvp_content_type, codename='change_rsvp')
        delete_permission = Permission.objects.get(content_type=rsvp_content_type, codename='delete_rsvp')

        self.privileged_user.role.user_permissions.add(add_permission, change_permission, delete_permission)

        OrganizerConfig.objects.create(
            event=self.event,
            person=self.organizer,
            is_creator=True
        )

        self.factory = APIRequestFactory()

        self.rsvp_list_view = RSVPViewSet.as_view({
            'get': 'list',
            'post': 'create'
        })

        self.rsvp_detail_view = RSVPViewSet.as_view({
            'get'
        })

    def test_unauthenticated_cannot_see_any_rsvp(self):
        request = self.get_request()

        response = self.rsvp_list_view(request)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_can_see_own_rsvps(self):
        request = self.as_unprivileged(self.get_request())

        response = self.rsvp_list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        assert all(rsvp['person'].split('/')[-2] == str(self.unprivileged_person.id) for rsvp in response.data)
        self.assertCountEqual([rsvp['event'].split('/')[-2] for rsvp in response.data],
                              [str(self.event.id), str(self.secondary_event.id)])

    @skip('TODO')
    def test_cannot_create_rsvp_as_unauthenticated(self):
        pass

    @skip('TODO')
    def test_can_create_rsvp_as_unprivileged(self):
        pass

    @skip('TODO')
    def test_can_modify_own_rsvp(self):
        pass


class EventTasksTestCase(TestCase):
    def setUp(self):
        now = timezone.now()

        self.calendar = Calendar.objects.create_calendar('default')

        self.creator = Person.objects.create_person("moi@moi.fr")
        self.event = Event.objects.create(
            name="Mon événement",
            start_time=now + timezone.timedelta(hours=2),
            end_time=now + timezone.timedelta(hours=3),
            contact_name="Moi",
            contact_email="monevenement@moi.fr",
            contact_phone="06 06 06 06 06",
            contact_hide_phone=False,
            location_name="ma maison",
            location_address1="Place denfert-rochereau",
            location_zip="75014",
            location_city="Paris",
            location_country="FR"
        )

        self.organizer_config = OrganizerConfig.objects.create(
            person=self.creator, event=self.event
        )

        self.attendee1 = Person.objects.create_person('person1@participants.fr')
        self.attendee2 = Person.objects.create_person('person2@participants.fr')
        self.attendee_no_notification = Person.objects.create_person('person3@participants.fr')

        self.rsvp1 = RSVP.objects.create(event=self.event, person=self.attendee1)
        self.rsvp2 = RSVP.objects.create(event=self.event, person=self.attendee2)
        self.rsvp3 = RSVP.objects.create(
            event=self.event,
            person=self.attendee_no_notification,
            notifications_enabled=False
        )

    def test_event_creation_mail(self):
        tasks.send_event_creation_notification(self.organizer_config.pk)

        self.assertEqual(len(mail.outbox), 1)

        message = mail.outbox[0]
        self.assertEqual(message.recipients(), ["moi@moi.fr"])

        text = message.body

        for item in ['name', 'location_name', 'short_address', 'contact_name', 'contact_phone']:
            self.assert_(getattr(self.event, item) in text, "{} missing in message".format(item))

    def test_rsvp_notification_mail(self):
        tasks.send_rsvp_notification(self.rsvp1.pk)

        self.assertEqual(len(mail.outbox), 2)

        attendee_message = mail.outbox[0]
        self.assertEqual(attendee_message.recipients(), ["person1@participants.fr"])

        text = attendee_message.body.replace('\n', '')
        mail_content = {
            'event name': self.event.name,
            'event link': front_url('view_event', kwargs={'pk': self.event.pk})
        }

        for name, value in mail_content.items():
            self.assert_(value in text, '{} missing from mail'.format(name))

        org_message = mail.outbox[1]
        self.assertEqual(org_message.recipients(), ["moi@moi.fr"])

        text = org_message.body.replace('\n', '')

        mail_content = {
            'attendee information': str(self.attendee1),
            'event name': self.event.name,
            'event management link': front_url('manage_event', kwargs={'pk': self.event.pk})
        }

        for name, value in mail_content.items():
            self.assert_(value in text, '{} missing from mail'.format(name))

    def test_changed_event_notification_mail(self):
        tasks.send_event_changed_notification(self.event.pk, ["information", "timing"])

        self.assertEqual(len(mail.outbox), 2)

        for message in mail.outbox:
            self.assertEqual(len(message.recipients()), 1)

        messages = {message.recipients()[0]: message for message in mail.outbox}

        self.assertCountEqual(messages.keys(), [self.attendee1.email, self.attendee2.email])

        for recipient, message in messages.items():
            text = message.body.replace('\n', '')

            self.assert_(self.event.name in text, 'event name not in message')
            self.assert_(
                front_url('quit_event', kwargs={'pk': self.event.pk}) in text,
                'quit event link not in message'
            )

            self.assert_(str(tasks.CHANGE_DESCRIPTION['information']) in text)
            self.assert_(str(tasks.CHANGE_DESCRIPTION['timing']) in text)
            self.assert_(str(tasks.CHANGE_DESCRIPTION['contact']) not in text)


class EventWorkerTestCase(TestCase):
    def setUp(self):
        self.worker = Client.objects.create_client(
            'worker'
        )

        self.worker.role.groups.add(Group.objects.get(name='workers'))

        self.unpublished_event = Event.objects.create(
            name='event',
            start_time=timezone.now() + timezone.timedelta(hours=2),
            end_time=timezone.now() + timezone.timedelta(hours=4),
            published=False
        )

        self.past_event = Event.objects.create(
            name='event',
            start_time=timezone.now() + timezone.timedelta(days=-2),
            end_time=timezone.now() + timezone.timedelta(days=-2, hours=4),
        )

        self.client.force_login(self.worker.role)

    def test_worker_can_get_unpublished_event(self):
        response = self.client.get('/legacy/events/{}/'.format(self.unpublished_event.pk))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['_id'], str(self.unpublished_event.pk))

    def test_worker_can_get_past_event(self):
        response = self.client.get('/legacy/events/{}/'.format(self.past_event.pk))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['_id'], str(self.past_event.pk))


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

        self.assertRedirects(res, reverse('payment_page', args=(payment.pk,)))

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

        self.assertRedirects(res, reverse('payment_page', args=(payment.pk,)))

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
