from django.test import TestCase
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geos import Point

from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status

from .models import Event, Calendar, RSVP
from people.models import Person
from .viewsets import LegacyEventViewSet


class BasicEventTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.calendar = Calendar.objects.create(label='test')

        cls.start_time = timezone.now()
        cls.end_time = cls.start_time + timezone.timedelta(hours=2)

    def test_can_create_event(self):

        event = Event.objects.create(
            name='Event test',
            calendar=self.calendar,
            start_time=self.start_time,
            end_time=self.end_time
        )

        self.assertEqual(event, Event.objects.get(name='Event test'))

    def test_cannot_create_without_dates(self):
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                    Event.objects.create(
                        name='Event test',
                        calendar=self.calendar,
                        start_time=self.start_time
                    )

        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Event.objects.create(
                    name='Event test 2',
                    calendar=self.calendar,
                    end_time=self.end_time
                )


class RSVPTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        calendar = Calendar.objects.create(label='test')

        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(hours=3)

        cls.event = Event.objects.create(
            name='Test',
            calendar=calendar,
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

        self.assertEquals(self.event.participants, 11)

        RSVP.objects.create(
            person=Person.objects.create(email='person2@domain.com'),
            event=self.event,
        )

        self.assertEqual(self.event.participants, 12)


class LegacyEventViewSetTestCase(TestCase):
    def setUp(self):
        self.calendar = Calendar.objects.create(label='calendar')

        self.event = Event.objects.create(
            name='event',
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(hours=4),
            calendar=self.calendar
        )

        self.unprivileged_person = Person.objects.create_person(
            email='jean.georges@domain.com',
            first_name='Jean',
            last_name='Georges',
        )

        self.adder_person = Person.objects.create_person(
            email='adder@adder.fr',
        )

        self.changer_person = Person.objects.create_person(
            email='changer@changer.fr'
        )

        self.one_event_person = Person.objects.create_person(
            email='event@event.com'
        )

        event_content_type = ContentType.objects.get_for_model(Event)
        add_permission = Permission.objects.get(content_type=event_content_type, codename='add_event')
        change_permission = Permission.objects.get(content_type=event_content_type, codename='change_event')

        self.adder_person.role.user_permissions.add(add_permission)
        self.changer_person.role.user_permissions.add(change_permission)
        self.event.organizers.add(self.one_event_person)

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
            'calendar': 'calendar',
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
        assert {'name', 'path', 'id', 'location', 'contact', 'tags', 'coordinates'}.issubset(item)

    def test_can_see_event_details_while_unauthenticated(self):
        request = self.factory.get('')
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

    def test_can_create_event_with_global_perm(self):
        request = self.factory.post('', data=self.new_event_data)
        force_authenticate(request, self.adder_person.role)

        response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        events = Event.objects.all()

        self.assertEqual(len(events), 2)

    def test_can_modify_event_with_global_perm(self):
        request = self.factory.patch('', data={
            'description': 'Plus mieux!'
        })

        force_authenticate(request, user=self.changer_person.role)

        response = self.detail_view(request, pk=self.event.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.event.refresh_from_db()

        self.assertEqual(self.event.description, 'Plus mieux!')

    def test_organizer_can_modify_event(self):
        request = self.factory.patch('', data={
            'description': 'Plus mieux!'
        })

        force_authenticate(request, user=self.one_event_person.role)

        response = self.detail_view(request, pk=self.event.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.event.refresh_from_db()

        self.assertEqual(self.event.description, 'Plus mieux!')


class FiltersTestCase(TestCase):
    def get_request(self, path='', data=None, **extra):
        return self.as_superuser(self.factory.get(path, data, **extra))

    def as_superuser(self, request):
        force_authenticate(request, self.superuser.role)
        return request

    def setUp(self):
        self.superuser = Person.objects.create_superperson('super@user.fr', None)

        calendar = Calendar.objects.create(label='Agenda')

        tz = timezone.get_default_timezone()

        self.paris_june_event = Event.objects.create(
            name='Paris+June',
            nb_id=1,
            start_time=tz.localize(timezone.datetime(2017, 6, 15, 18)),
            end_time=tz.localize(timezone.datetime(2017, 6, 15, 22)),
            coordinates=Point(2.349722, 48.853056),  # ND de Paris
            calendar=calendar
        )

        self.amiens_july_event = Event.objects.create(
            name='Amiens+July',
            nb_path='/amiens_july',
            start_time=tz.localize(timezone.datetime(2017, 7, 15, 18)),
            end_time=tz.localize(timezone.datetime(2017, 7, 15, 22)),
            coordinates=Point(2.301944, 49.8944),  # ND d'Amiens
            calendar=calendar
        )

        self.marseille_august_event = Event.objects.create(
            name='Marseille+August',
            start_time=tz.localize(timezone.datetime(2017, 8, 15, 18)),
            end_time=tz.localize(timezone.datetime(2017, 8, 15, 22)),
            coordinates=Point(5.36472, 43.30028),  # Saint-Marie-Majeure de Marseille
            calendar=calendar
        )

        self.eiffel_coordinates = [2.294444, 48.858333]

        self.factory = APIRequestFactory()
        self.list_view = LegacyEventViewSet.as_view({
            'get': 'list',
            'post': 'create'
        })

        self.detail_view = LegacyEventViewSet.as_view({
            'get': 'retrieve',
            'put': 'update',
            'patch': 'partial_update',
            'delete': 'destroy',
        })

    def test_can_query_by_pk(self):
        request = self.get_request()

        response = self.detail_view(request, pk=self.paris_june_event.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.paris_june_event.name)

    def test_can_query_by_nb_id(self):
        request = self.get_request()

        response = self.detail_view(request, pk=str(self.paris_june_event.nb_id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['_id'], str(self.paris_june_event.pk))

    def test_filter_coordinates_no_results(self):
        # la tour eiffel est à plus d'un kilomètre de Notre-Dame
        filter_string = '{"maxDistance": 1000, "coordinates": %r}' % (self.eiffel_coordinates,)

        request = self.factory.get('', data={
            'closeTo': filter_string
        })

        response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('_items', response.data)
        self.assertEqual(len(response.data['_items']), 0)

    def test_filter_coordinates_one_result(self):
        # la tour eiffel est à moins de 10 km de Notre-Dame
        filter_string = '{"maxDistance": 10000, "coordinates": %r}' % (self.eiffel_coordinates,)

        request = self.factory.get('', data={
            'closeTo': filter_string,
        })

        response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('_items', response.data)
        self.assertEqual(len(response.data['_items']), 1)
        self.assertEqual(response.data['_items'][0]['_id'], str(self.paris_june_event.pk))

    def test_filter_by_path(self):
        request = self.factory.get('', data={
            'path': '/amiens_july',
        })

        response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('_items', response.data)
        self.assertEqual(len(response.data['_items']), 1)
        self.assertEqual(response.data['_items'][0]['_id'], str(self.amiens_july_event.pk))
