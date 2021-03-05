from django.utils import timezone
from rest_framework.test import APITestCase
from unittest.mock import patch

from agir.events.models import Event, RSVP
from agir.people.models import Person, PersonForm


class RSVPEventAPITestCase(APITestCase):
    def setUp(self):
        self.person = Person.objects.create(
            email="person@example.com",
            create_role=True,
            is_insoumise=True,
            is_2022=True,
        )
        self.start_time = timezone.now()
        self.end_time = self.start_time + timezone.timedelta(hours=2)

    def test_anonymous_person_cannot_rsvp(self):
        self.client.logout()
        event = Event.objects.create(
            name="Event", start_time=self.start_time, end_time=self.end_time
        )
        res = self.client.post(f"/api/evenements/{event.pk}/inscription/")
        self.assertEqual(res.status_code, 403)
        self.assertIn("redirectTo", res.data)

    def test_2022_person_cannot_rsvp_insoumise_event(self):
        person_2022 = Person.objects.create(
            email="2022@example.com",
            create_role=True,
            is_insoumise=False,
            is_2022=True,
        )
        event = Event.objects.create(
            name="Event",
            start_time=self.start_time,
            end_time=self.end_time,
            for_users=Event.FOR_USERS_INSOUMIS,
        )
        self.client.force_login(person_2022.role)
        res = self.client.post(f"/api/evenements/{event.pk}/inscription/")
        self.assertEqual(res.status_code, 403)
        self.assertIn("redirectTo", res.data)

    def test_insoumise_person_cannot_rsvp_2022_event(self):
        person_insoumise = Person.objects.create(
            email="insoumise@example.com",
            create_role=True,
            is_insoumise=True,
            is_2022=False,
        )
        event = Event.objects.create(
            name="Event",
            start_time=self.start_time,
            end_time=self.end_time,
            for_users=Event.FOR_USERS_2022,
        )
        self.client.force_login(person_insoumise.role)
        res = self.client.post(f"/api/evenements/{event.pk}/inscription/")
        self.assertEqual(res.status_code, 403)
        self.assertIn("redirectTo", res.data)

    def test_person_cannot_rsvp_event_with_subscription_form(self):
        subscription_form = PersonForm.objects.create()
        event = Event.objects.create(
            name="Event",
            start_time=self.start_time,
            end_time=self.end_time,
            subscription_form_id=subscription_form.pk,
        )
        self.client.force_login(self.person.role)
        res = self.client.post(f"/api/evenements/{event.pk}/inscription/")
        self.assertEqual(res.status_code, 403)
        self.assertIn("redirectTo", res.data)

    def test_person_cannot_rsvp_if_already_participant(self):
        event = Event.objects.create(
            name="Event", start_time=self.start_time, end_time=self.end_time,
        )
        RSVP.objects.create(
            event=event, person=self.person, status=RSVP.STATUS_CONFIRMED,
        )
        self.client.force_login(self.person.role)
        res = self.client.post(f"/api/evenements/{event.pk}/inscription/")
        self.assertEqual(res.status_code, 403)
        self.assertIn("redirectTo", res.data)

    def test_person_cannot_rsvp_if_event_is_not_free(self):
        event = Event.objects.create(
            name="Event",
            start_time=self.start_time,
            end_time=self.end_time,
            payment_parameters='{"price":10}',
        )
        RSVP.objects.create(
            event=event, person=self.person, status=RSVP.STATUS_CONFIRMED,
        )
        self.client.force_login(self.person.role)
        res = self.client.post(f"/api/evenements/{event.pk}/inscription/")
        self.assertEqual(res.status_code, 403)
        self.assertIn("redirectTo", res.data)

    def test_authenticated_person_can_rsvp_available_event(self):
        event = Event.objects.create(
            name="Event", start_time=self.start_time, end_time=self.end_time,
        )
        self.client.force_login(self.person.role)
        res = self.client.post(f"/api/evenements/{event.pk}/inscription/")
        self.assertEqual(res.status_code, 201)

    @patch("agir.events.views.api_views.rsvp_to_free_event")
    def test_rsvp_to_free_event_is_called_upon_joining(self, rsvp_to_free_event):
        event = Event.objects.create(
            name="Event", start_time=self.start_time, end_time=self.end_time,
        )
        self.client.force_login(self.person.role)
        rsvp_to_free_event.assert_not_called()
        res = self.client.post(f"/api/evenements/{event.pk}/inscription/")
        self.assertEqual(res.status_code, 201)
        rsvp_to_free_event.assert_called()

    def test_rsvp_is_created_upoin_rsvping(self):
        event = Event.objects.create(
            name="Event", start_time=self.start_time, end_time=self.end_time,
        )
        self.client.force_login(self.person.role)
        self.assertFalse(RSVP.objects.filter(event=event, person=self.person,).exists())
        res = self.client.post(f"/api/evenements/{event.pk}/inscription/")
        self.assertEqual(res.status_code, 201)
        self.assertTrue(RSVP.objects.filter(event=event, person=self.person,).exists())
