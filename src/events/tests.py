from django.test import TestCase
from django.db import IntegrityError, transaction
from datetime import datetime
import pytz

from .models import Event, Calendar


class BasicEventTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        Calendar.objects.create(label='test')

    def test_can_create_event(self):
        utc = pytz.timezone('UTC')

        event = Event.objects.create(
            name='Event test',
            calendar=Calendar.objects.get_by_natural_key('test'),
            start_time=utc.localize(datetime(2012, 4, 21)),
            end_time=utc.localize(datetime(2017, 4, 23))
        )

        self.assertEqual(event, Event.objects.get(name='Event test'))

    def test_cannot_create_without_dates(self):
        date = pytz.timezone('UTC').localize(datetime(2017, 5, 10))
        calendar = Calendar.objects.get_by_natural_key('test')

        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                    Event.objects.create(
                        name='Event test',
                        calendar=calendar,
                        start_time=date
                    )

        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Event.objects.create(
                    name='Event test 2',
                    calendar=calendar,
                    end_time=date
                )
