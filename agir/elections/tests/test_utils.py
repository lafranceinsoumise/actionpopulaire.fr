from datetime import timedelta
from unittest import TestCase

from agir.elections.utils import TREVE_ELECTORALE, is_forbidden_during_treve_event
from agir.events.models import Event, EventSubtype


class IsForbiddenDuringTreveEventTestCase(TestCase):
    def setUp(self):
        (self.authorized_subtype, created) = EventSubtype.objects.get_or_create(
            label="soiree-electorale"
        )
        (self.unauthorized_subtype, created) = EventSubtype.objects.get_or_create(
            label="porte-a-porte"
        )
        self.treve_start, self.treve_end, *rest = TREVE_ELECTORALE[0]

    def test_before_treve_event(self):
        event = Event.objects.create(
            start_time=self.treve_start - timedelta(days=5),
            end_time=self.treve_start - timedelta(days=4),
            subtype_id=self.unauthorized_subtype.id,
        )
        result = is_forbidden_during_treve_event(event)
        self.assertFalse(result)

    def test_after_treve_event(self):
        event = Event.objects.create(
            start_time=self.treve_end + timedelta(days=4),
            end_time=self.treve_end + timedelta(days=5),
            subtype_id=self.unauthorized_subtype.id,
        )
        result = is_forbidden_during_treve_event(event)
        self.assertFalse(result)

    def test_during_treve_event(self):
        event = Event.objects.create(
            start_time=self.treve_start + timedelta(minutes=4),
            end_time=self.treve_end - timedelta(minutes=4),
            subtype_id=self.unauthorized_subtype.id,
        )
        result = is_forbidden_during_treve_event(event)
        self.assertTrue(result)
        event = Event.objects.create(
            start_time=self.treve_start + timedelta(minutes=4),
            end_time=self.treve_end + timedelta(minutes=4),
            subtype_id=self.unauthorized_subtype.id,
        )
        result = is_forbidden_during_treve_event(event)
        self.assertTrue(result)
        event = Event.objects.create(
            start_time=self.treve_start - timedelta(minutes=4),
            end_time=self.treve_end - timedelta(minutes=4),
            subtype_id=self.unauthorized_subtype.id,
        )
        result = is_forbidden_during_treve_event(event)
        self.assertTrue(result)

    def test_authorized_event_during_treve(self):
        event = Event.objects.create(
            start_time=self.treve_start + timedelta(minutes=4),
            end_time=self.treve_end - timedelta(minutes=4),
            subtype_id=self.authorized_subtype.id,
        )
        result = is_forbidden_during_treve_event(event)
        self.assertFalse(result)

    def test_uuid_event_argument(self):
        event = Event.objects.create(
            start_time=self.treve_start + timedelta(minutes=4),
            end_time=self.treve_end - timedelta(minutes=4),
            subtype_id=self.authorized_subtype.id,
        )
        result = is_forbidden_during_treve_event(event.pk)
        self.assertFalse(result)

    def test_uuid_dict_argument(self):
        result = is_forbidden_during_treve_event(
            {
                "start_time": self.treve_start + timedelta(minutes=4),
                "end_time": self.treve_end - timedelta(minutes=4),
                "subtype": self.authorized_subtype,
            }
        )
        self.assertFalse(result)
