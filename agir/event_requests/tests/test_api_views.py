from django.utils import timezone
from rest_framework.test import APITestCase

from agir.event_requests.models import (
    EventSpeaker,
    EventRequest,
    EventThemeType,
    EventTheme,
    EventSpeakerRequest,
)
from agir.events.models import EventSubtype
from agir.lib.utils import front_url
from agir.people.models import Person


class EventSpeakerRetrieveUpdateAPITestCase(APITestCase):
    endpoint = front_url("api_event_speaker_retrieve_update")

    def setUp(self):
        self.valid_patch_data = {"available": False}
        self.non_speaker_person = Person.objects.create_person(
            "non-speaker@pers.on", create_role=True, display_name="Non-Speaker Person"
        )
        self.event_speaker = EventSpeaker.objects.create(
            available=True,
            person=Person.objects.create_person(
                "speaker@pers.on", create_role=True, display_name="Speaker Person"
            ),
        )

    def test_anonymous_user_cannot_retrieve_anything(self):
        self.client.logout()
        res = self.client.get(self.endpoint)
        self.assertEqual(res.status_code, 401)

    def test_non_speaker_person_cannot_retrieve_anything(self):
        self.client.force_login(self.non_speaker_person.role)
        res = self.client.get(self.endpoint)
        self.assertEqual(res.status_code, 404)

    def test_authenticated_speaker_person_can_retrieve_her_data(self):
        self.client.force_login(self.event_speaker.person.role)
        res = self.client.get(self.endpoint)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["id"], str(self.event_speaker.id))

    def test_anonymous_user_cannot_update_data(self):
        self.client.logout()
        res = self.client.patch(self.endpoint, data=self.valid_patch_data)
        self.assertEqual(res.status_code, 401)

    def test_non_speaker_person_cannot_update_data(self):
        self.client.force_login(self.non_speaker_person.role)
        res = self.client.patch(self.endpoint, data=self.valid_patch_data)
        self.assertEqual(res.status_code, 404)

    def test_authenticated_user_can_update_her_data(self):
        self.client.force_login(self.event_speaker.person.role)
        self.assertNotEqual(
            self.valid_patch_data["available"], self.event_speaker.available
        )
        res = self.client.patch(self.endpoint, data=self.valid_patch_data)
        self.assertEqual(res.status_code, 200)
        self.event_speaker.refresh_from_db()
        self.assertEqual(
            self.valid_patch_data["available"], self.event_speaker.available
        )


class EventSpeakerRequestRetrieveUpdateAPITestCase(APITestCase):
    def setUp(self):
        self.valid_patch_data = {"available": True}
        self.non_speaker_person = Person.objects.create_person(
            "non-speaker@pers.on", create_role=True, display_name="Non-Speaker Person"
        )
        self.event_speaker = EventSpeaker.objects.create(
            available=True,
            person=Person.objects.create_person(
                "speaker@pers.on", create_role=True, display_name="Speaker Person"
            ),
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
        self.event_speaker_request = EventSpeakerRequest.objects.create(
            event_speaker=self.event_speaker,
            event_request=self.pending_event_request,
            datetime=self.pending_event_request.datetimes[0],
            available=None,
            accepted=False,
        )
        self.endpoint = front_url(
            "api_event_speaker_request_retrieve_update",
            kwargs={"pk": self.event_speaker_request.pk},
        )

    def test_anonymous_user_cannot_retrieve_anything(self):
        self.client.logout()
        res = self.client.get(self.endpoint)
        self.assertEqual(res.status_code, 401)

    def test_non_speaker_person_cannot_retrieve_anything(self):
        self.client.force_login(self.non_speaker_person.role)
        res = self.client.get(self.endpoint)
        self.assertEqual(res.status_code, 403)

    def test_authenticated_speaker_person_can_retrieve_her_data(self):
        self.client.force_login(self.event_speaker.person.role)
        res = self.client.get(self.endpoint)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["id"], str(self.event_speaker_request.id))

    def test_anonymous_user_cannot_update_data(self):
        self.client.logout()
        res = self.client.patch(self.endpoint, data=self.valid_patch_data)
        self.assertEqual(res.status_code, 401)

    def test_non_speaker_person_cannot_update_data(self):
        self.client.force_login(self.non_speaker_person.role)
        res = self.client.patch(self.endpoint, data=self.valid_patch_data)
        self.assertEqual(res.status_code, 403)

    def test_authenticated_user_can_update_her_data(self):
        self.client.force_login(self.event_speaker.person.role)
        self.assertNotEqual(
            self.valid_patch_data["available"], self.event_speaker_request.available
        )
        res = self.client.patch(self.endpoint, data=self.valid_patch_data)
        self.assertEqual(res.status_code, 200)
        self.event_speaker_request.refresh_from_db()
        self.assertEqual(
            self.valid_patch_data["available"], self.event_speaker_request.available
        )
