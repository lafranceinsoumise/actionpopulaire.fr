from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from django.utils import timezone

from agir.event_requests.models import (
    EventSpeaker,
    EventThemeType,
    EventTheme,
    EventRequest,
    EventSpeakerRequest,
)
from agir.events.models import EventSubtype
from agir.people.models import Person


class EventSpeakerPermissionsTestCase(TestCase):
    view_permission = "event_requests.view_event_speaker"
    change_permission = "event_requests.change_event_speaker"

    def setUp(self):
        self.anonymous = AnonymousUser()
        self.non_owner = Person.objects.create_person(
            "non-speaker@pers.on", create_role=True, display_name="Non-Speaker Person"
        )
        self.owner = Person.objects.create_person(
            "speaker@pers.on", create_role=True, display_name="Speaker Person"
        )
        self.event_speaker = EventSpeaker.objects.create(
            available=True, person=self.owner
        )

    def test_anonymous_cannot_view(self):
        self.assertFalse(
            self.anonymous.has_perm(self.view_permission, self.event_speaker)
        )

    def test_non_owner_cannot_view(self):
        self.assertFalse(
            self.non_owner.has_perm(self.view_permission, self.event_speaker)
        )

    def test_owner_can_view(self):
        self.assertTrue(self.owner.has_perm(self.view_permission, self.event_speaker))

    def test_anonymous_cannot_change(self):
        self.assertFalse(
            self.anonymous.has_perm(self.change_permission, self.event_speaker)
        )

    def test_non_owner_cannot_change(self):
        self.assertFalse(
            self.non_owner.has_perm(self.change_permission, self.event_speaker)
        )

    def test_owner_can_change(self):
        self.assertTrue(self.owner.has_perm(self.change_permission, self.event_speaker))


class EventSpeakerRequestPermissionsTestCase(TestCase):
    view_permission = "event_requests.view_event_speaker_request"
    change_permission = "event_requests.change_event_speaker_request"

    def setUp(self):
        self.anonymous = AnonymousUser()

        self.non_owner = Person.objects.create_person(
            "non-speaker@pers.on", create_role=True, display_name="Non-Speaker Person"
        )
        self.owner = Person.objects.create_person(
            "speaker@pers.on", create_role=True, display_name="Speaker Person"
        )
        self.event_speaker = EventSpeaker.objects.create(
            available=True,
            person=self.owner,
        )
        event_subytpe = EventSubtype.objects.create(label="Event subtype")
        theme_type = EventThemeType.objects.create(
            name="Theme type", event_subtype=event_subytpe
        )
        theme = EventTheme.objects.create(name="Theme", event_theme_type=theme_type)
        theme.event_speakers.add(self.event_speaker)

        self.pending_event_request = EventRequest.objects.create(
            event_theme=theme,
            datetimes=[timezone.now()],
            location_zip="67000",
            location_city="Strasbourg",
            location_country="FR",
            status=EventRequest.Status.PENDING,
        )
        self.done_event_request = EventRequest.objects.create(
            event_theme=theme,
            datetimes=[timezone.now()],
            location_zip="67000",
            location_city="Strasbourg",
            location_country="FR",
            status=EventRequest.Status.DONE,
        )
        self.unanswerable_event_speaker_request = EventSpeakerRequest.objects.create(
            event_speaker=self.event_speaker,
            event_request=self.done_event_request,
            datetime=self.done_event_request.datetimes[0],
            available=None,
            accepted=False,
        )
        self.answerable_event_speaker_request = EventSpeakerRequest.objects.create(
            event_speaker=self.event_speaker,
            event_request=self.pending_event_request,
            datetime=self.pending_event_request.datetimes[0],
            available=None,
            accepted=False,
        )

    def test_anonymous_cannot_view(self):
        self.assertFalse(
            self.anonymous.has_perm(
                self.view_permission, self.unanswerable_event_speaker_request
            )
        )
        self.assertFalse(
            self.anonymous.has_perm(
                self.view_permission, self.answerable_event_speaker_request
            )
        )

    def test_non_owner_cannot_view(self):
        self.assertFalse(
            self.non_owner.has_perm(
                self.view_permission, self.unanswerable_event_speaker_request
            )
        )
        self.assertFalse(
            self.non_owner.has_perm(
                self.view_permission, self.answerable_event_speaker_request
            )
        )

    def test_owner_can_view(self):
        self.assertTrue(
            self.owner.has_perm(
                self.view_permission, self.unanswerable_event_speaker_request
            )
        )
        self.assertTrue(
            self.owner.has_perm(
                self.view_permission, self.answerable_event_speaker_request
            )
        )

    def test_anonymous_cannot_change(self):
        self.assertFalse(
            self.anonymous.has_perm(
                self.change_permission, self.unanswerable_event_speaker_request
            )
        )
        self.assertFalse(
            self.anonymous.has_perm(
                self.change_permission, self.answerable_event_speaker_request
            )
        )

    def test_non_owner_cannot_change(self):
        self.assertFalse(
            self.non_owner.has_perm(
                self.change_permission, self.unanswerable_event_speaker_request
            )
        )
        self.assertFalse(
            self.non_owner.has_perm(
                self.change_permission, self.answerable_event_speaker_request
            )
        )

    def test_owner_cannot_change_non_answerable_request(self):
        self.assertFalse(
            self.owner.has_perm(
                self.change_permission, self.unanswerable_event_speaker_request
            )
        )

    def test_owner_can_change_answerable_request(self):
        self.assertTrue(
            self.owner.has_perm(
                self.change_permission, self.answerable_event_speaker_request
            )
        )
