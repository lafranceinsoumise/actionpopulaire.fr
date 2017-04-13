from django.test import TestCase
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
