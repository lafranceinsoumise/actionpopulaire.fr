from datetime import timedelta
from unittest import TestCase

from agir.elections.utils import (
    TREVE_ELECTORALE,
    is_forbidden_during_treve_event,
    OVERSEAS_AND_AMERICAS,
)
from agir.events.models import Event, EventSubtype


class IsForbiddenDuringTreveEventTestCase(TestCase):
    def setUp(self):
        (self.authorized_subtype, created) = EventSubtype.objects.get_or_create(
            label="soiree-electorale"
        )
        (self.unauthorized_subtype, created) = EventSubtype.objects.get_or_create(
            label="porte-a-porte"
        )
        self.treve_country_code = OVERSEAS_AND_AMERICAS[0]
        self.timezone = "America/Argentina/Buenos_Aires"
        self.authorized_country_code = "UK"
        self.treve_start, self.treve_end, *rest = TREVE_ELECTORALE[
            "OVERSEAS_AND_AMERICAS"
        ][0]

    def test_before_treve_event(self):
        event_data = {
            "start_time": self.treve_start - timedelta(days=5),
            "end_time": self.treve_start - timedelta(days=4),
            "subtype": self.unauthorized_subtype,
            "location_country": self.treve_country_code,
            "timezone": self.timezone,
        }
        result = is_forbidden_during_treve_event(event_data)
        self.assertFalse(result)

    def test_after_treve_event(self):
        event_data = {
            "start_time": self.treve_end + timedelta(days=4),
            "end_time": self.treve_end + timedelta(days=5),
            "subtype": self.unauthorized_subtype,
            "location_country": self.treve_country_code,
            "timezone": self.timezone,
        }
        result = is_forbidden_during_treve_event(event_data)
        self.assertFalse(result)

    def test_during_treve_event_creation(self):
        event_data = {
            "start_time": self.treve_start + timedelta(minutes=4),
            "end_time": self.treve_end - timedelta(minutes=4),
            "subtype": self.unauthorized_subtype,
            "location_country": self.treve_country_code,
            "timezone": self.timezone,
        }
        result = is_forbidden_during_treve_event(event_data)
        self.assertTrue(result)
        event_data = {
            "start_time": self.treve_start + timedelta(minutes=4),
            "end_time": self.treve_end + timedelta(minutes=4),
            "subtype": self.unauthorized_subtype,
            "location_country": self.treve_country_code,
            "timezone": self.timezone,
        }
        result = is_forbidden_during_treve_event(event_data)
        self.assertTrue(result)
        event_data = {
            "start_time": self.treve_start - timedelta(minutes=4),
            "end_time": self.treve_end - timedelta(minutes=4),
            "subtype": self.unauthorized_subtype,
            "location_country": self.treve_country_code,
            "timezone": self.timezone,
        }
        result = is_forbidden_during_treve_event(event_data)
        self.assertTrue(result)

    def test_during_treve_event_update(self):
        event_data = {
            "start_time": self.treve_start + timedelta(minutes=4),
            "end_time": self.treve_end - timedelta(minutes=4),
            "subtype_id": self.unauthorized_subtype.id,
            "location_country": self.treve_country_code,
            "timezone": self.timezone,
        }
        event = Event.objects.create(**event_data)
        event_data = {"id": event.pk}
        result = is_forbidden_during_treve_event(event_data)
        self.assertTrue(result)
        event_data = {
            **event_data,
            "start_time": self.treve_start + timedelta(minutes=4),
            "end_time": self.treve_end + timedelta(minutes=4),
        }
        result = is_forbidden_during_treve_event(event_data)
        self.assertTrue(result)
        event_data = {
            **event_data,
            "start_time": self.treve_start - timedelta(minutes=4),
            "end_time": self.treve_end - timedelta(minutes=4),
        }
        result = is_forbidden_during_treve_event(event_data)
        self.assertTrue(result)

    def test_authorized_event_subtype_during_treve(self):
        event_data = {
            "start_time": self.treve_start + timedelta(minutes=4),
            "end_time": self.treve_end - timedelta(minutes=4),
            "subtype": self.authorized_subtype,
            "location_country": self.treve_country_code,
            "timezone": self.timezone,
        }
        result = is_forbidden_during_treve_event(event_data)
        self.assertFalse(result)
