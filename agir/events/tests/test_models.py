from django.test import TestCase
from django.db import IntegrityError, transaction
from django.utils import timezone

from agir.people.models import Person

from ..models import Event, Calendar, RSVP


class BasicEventTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.calendar = Calendar.objects.create_calendar("test")

        cls.start_time = timezone.now()
        cls.end_time = cls.start_time + timezone.timedelta(hours=2)

    def test_can_create_event(self):
        event = Event.objects.create(
            name="Event test", start_time=self.start_time, end_time=self.end_time
        )

        self.assertEqual(event, Event.objects.get(name="Event test"))

    def test_cannot_create_without_dates(self):
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Event.objects.create(name="Event test", start_time=self.start_time)

        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Event.objects.create(name="Event test 2", end_time=self.end_time)


class RSVPTestCase(TestCase):
    def setUp(self):
        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(hours=3)
        self.event = Event.objects.create(
            name="Test", start_time=start_time, end_time=end_time
        )
        self.person = Person.objects.create_insoumise(email="marc.machin@truc.com")

    def test_create_rsvps(self):
        rsvp = RSVP.objects.create(person=self.person, event=self.event)

        self.assertCountEqual([rsvp], self.person.rsvps.all())
        self.assertCountEqual([rsvp], self.event.rsvps.all())
        self.assertCountEqual([self.person], self.event.confirmed_attendees)

    def test_cannot_create_without_person(self):
        with self.assertRaises(IntegrityError):
            RSVP.objects.create(event=self.event)

    def test_cannot_create_without_event(self):
        with self.assertRaises(IntegrityError):
            RSVP.objects.create(person=self.person)

    def test_unique_rsvp(self):
        RSVP.objects.create(person=self.person, event=self.event)

        with self.assertRaises(IntegrityError):
            RSVP.objects.create(person=self.person, event=self.event)

    def test_participants_count(self):
        RSVP.objects.create(person=self.person, event=self.event, guests=10)

        self.assertEqual(self.event.participants, 11)

        RSVP.objects.create(
            person=Person.objects.create_insoumise(email="person2@domain.com"),
            event=self.event,
        )

        # on supprime la valeur en cache
        del self.event.all_attendee_count

        self.assertEqual(self.event.participants, 12)
