from unittest.mock import patch

from django.utils import timezone
from rest_framework.test import APITestCase

from agir.events.models import EventSubtype, OrganizerConfig
from agir.groups.models import SupportGroup, Membership
from agir.lib.tests.mixins import create_location, get_random_object


class CreateEventAPITestCase(APITestCase):
    def setUp(self):
        self.managed_group = SupportGroup.objects.create()
        self.unmanaged_group = SupportGroup.objects.create()
        self.person = Person.objects.create(
            email="person@example.com", create_role=True,
        )
        Membership.objects.create(
            supportgroup=self.managed_group,
            person=self.person,
            membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )
        self.start_time = timezone.now() + timezone.timedelta(days=3)
        self.end_time = timezone.now() + timezone.timedelta(days=3, hours=4)
        self.location = create_location()
        self.subtype = get_random_object(EventSubtype)
        self.valid_data = {
            "name": "Nouvel événement",
            "startTime": str(self.start_time),
            "endTime": str(self.end_time),
            "timezone": timezone.get_default_timezone_name(),
            "contact": {
                "name": "Quelqu'un",
                "email": "quelquun@agir.test",
                "phone": "0600000000",
                "hidePhone": True,
            },
            "location": {
                "name": self.location["location_name"],
                "address1": self.location["location_address1"],
                "address2": self.location["location_address2"],
                "zip": self.location["location_zip"],
                "city": self.location["location_city"],
                "country": self.location["location_country"],
            },
            "forUsers": Event.FOR_USERS_INSOUMIS,
            "subtype": self.subtype.id,
            "organizerGroup": self.managed_group.id,
            "legal": "{}",
            "onlineUrl": "https://visio.lafranceinsoumise.fr/abcdef",
        }

    def test_anonymous_person_cannot_post(self):
        self.client.logout()
        res = self.client.post("/api/evenements/creer/", data=self.valid_data)
        self.assertEqual(res.status_code, 401)

    def test_authenticated_user_can_post(self):
        self.client.force_login(self.person.role)
        res = self.client.post("/api/evenements/creer/", data=self.valid_data)
        self.assertEqual(res.status_code, 201)

    def test_event_is_created_upon_posting_valid_data(self):
        self.client.force_login(self.person.role)
        initial_event_length = Event.objects.all().count()
        res = self.client.post("/api/evenements/creer/", data=self.valid_data)
        self.assertEqual(res.status_code, 201)
        self.assertIn("id", res.data)
        self.assertEqual(Event.objects.all().count(), initial_event_length + 1)

    def test_organizer_config_is_created_upon_posting_valid_data_with_managed_group(
        self,
    ):
        self.client.force_login(self.person.role)
        res = self.client.post("/api/evenements/creer/", data=self.valid_data)
        self.assertEqual(res.status_code, 201)
        self.assertIn("id", res.data)
        organizer_config = OrganizerConfig.objects.filter(
            event_id=res.data["id"],
            as_group_id=self.valid_data["organizerGroup"],
            person=self.person,
        )
        self.assertEqual(organizer_config.count(), 1)

    def test_organizer_config_is_created_upon_posting_valid_data_without_group(self):
        self.client.force_login(self.person.role)
        res = self.client.post(
            "/api/evenements/creer/", data={**self.valid_data, "organizerGroup": None}
        )
        self.assertEqual(res.status_code, 201)
        self.assertIn("id", res.data)
        organizer_config = OrganizerConfig.objects.filter(
            event_id=res.data["id"], as_group=None, person=self.person,
        )
        self.assertEqual(organizer_config.count(), 1)

    def test_rsvp_is_created_upon_posting_valid_data(self):
        self.client.force_login(self.person.role)
        res = self.client.post("/api/evenements/creer/", data=self.valid_data)
        self.assertEqual(res.status_code, 201)
        self.assertIn("id", res.data)
        rsvp = OrganizerConfig.objects.filter(
            event_id=res.data["id"], person=self.person,
        )
        self.assertEqual(rsvp.count(), 1)

    @patch("agir.events.tasks.send_event_creation_notification.delay")
    def test_event_creation_notification_task_is_created_upon_posting_valid_data(
        self, send_event_creation_notification
    ):
        send_event_creation_notification.assert_not_called()
        self.client.force_login(self.person.role)
        res = self.client.post("/api/evenements/creer/", data=self.valid_data)
        self.assertEqual(res.status_code, 201)
        self.assertIn("id", res.data)
        send_event_creation_notification.assert_called_once()

    @patch("agir.events.tasks.geocode_event.delay")
    def test_geocoding_task_is_created_upon_posting_valid_data(self, geocode_event):
        geocode_event.assert_not_called()
        self.client.force_login(self.person.role)
        res = self.client.post("/api/evenements/creer/", data=self.valid_data)
        self.assertEqual(res.status_code, 201)
        self.assertIn("id", res.data)
        geocode_event.assert_called_once()

    @patch("agir.groups.tasks.notify_new_group_event.delay")
    def test_notify_new_group_event_task_is_created_upon_posting_valid_data_with_organizer_group(
        self, notify_new_group_event
    ):
        notify_new_group_event.assert_not_called()
        self.client.force_login(self.person.role)
        res = self.client.post("/api/evenements/creer/", data=self.valid_data)
        self.assertEqual(res.status_code, 201)
        self.assertIn("id", res.data)
        notify_new_group_event.assert_called_once()

    @patch("agir.groups.tasks.send_new_group_event_email.delay")
    def test_send_new_group_event_email_task_is_created_upon_posting_valid_data_with_organizer_group(
        self, send_new_group_event_email
    ):
        send_new_group_event_email.assert_not_called()
        self.client.force_login(self.person.role)
        res = self.client.post("/api/evenements/creer/", data=self.valid_data)
        self.assertEqual(res.status_code, 201)
        self.assertIn("id", res.data)
        send_new_group_event_email.assert_called_once()

    @patch("agir.groups.tasks.notify_new_group_event.delay")
    def test_notify_new_group_event_task_is_not_created_upon_posting_valid_data_without_organizer_group(
        self, notify_new_group_event
    ):
        notify_new_group_event.assert_not_called()
        self.client.force_login(self.person.role)
        res = self.client.post(
            "/api/evenements/creer/", data={**self.valid_data, "organizerGroup": None}
        )
        self.assertEqual(res.status_code, 201)
        self.assertIn("id", res.data)
        notify_new_group_event.assert_not_called()

    @patch("agir.groups.tasks.send_new_group_event_email.delay")
    def test_send_new_group_event_email_task_is_not_created_upon_posting_valid_data_without_organizer_group(
        self, send_new_group_event_email
    ):
        send_new_group_event_email.assert_not_called()
        self.client.force_login(self.person.role)
        res = self.client.post(
            "/api/evenements/creer/", data={**self.valid_data, "organizerGroup": None}
        )
        self.assertEqual(res.status_code, 201)
        self.assertIn("id", res.data)
        send_new_group_event_email.assert_not_called()

    def test_event_is_not_created_with_missing_name(self):
        self.client.force_login(self.person.role)
        res = self.client.post(
            "/api/evenements/creer/", data={**self.valid_data, "name": ""}
        )
        self.assertEqual(res.status_code, 422)
        self.assertIn("name", res.data)

    def test_event_is_not_created_with_too_short_name(self):
        self.client.force_login(self.person.role)
        res = self.client.post(
            "/api/evenements/creer/", data={**self.valid_data, "name": "A"}
        )
        self.assertEqual(res.status_code, 422)
        self.assertIn("name", res.data)

    def test_event_is_not_created_with_too_long_name(self):
        self.client.force_login(self.person.role)
        res = self.client.post(
            "/api/evenements/creer/", data={**self.valid_data, "name": "A" * 101}
        )
        self.assertEqual(res.status_code, 422)
        self.assertIn("name", res.data)

    def test_event_is_not_created_with_missing_start_time(self):
        self.client.force_login(self.person.role)
        res = self.client.post(
            "/api/evenements/creer/", data={**self.valid_data, "startTime": ""}
        )
        self.assertEqual(res.status_code, 422)
        self.assertIn("startTime", res.data)

    def test_event_is_not_created_with_invalid_start_time(self):
        self.client.force_login(self.person.role)
        res = self.client.post(
            "/api/evenements/creer/",
            data={**self.valid_data, "startTime": "not a date"},
        )
        self.assertEqual(res.status_code, 422)
        self.assertIn("startTime", res.data)

    def test_event_is_not_created_with_missing_end_time(self):
        self.client.force_login(self.person.role)
        res = self.client.post(
            "/api/evenements/creer/", data={**self.valid_data, "endTime": ""}
        )
        self.assertEqual(res.status_code, 422)
        self.assertIn("endTime", res.data)

    def test_event_is_not_created_with_invalid_end_time(self):
        self.client.force_login(self.person.role)
        res = self.client.post(
            "/api/evenements/creer/", data={**self.valid_data, "endTime": "not a date"}
        )
        self.assertEqual(res.status_code, 422)
        self.assertIn("endTime", res.data)

    def test_event_is_not_created_with_event_duration_longer_than_7_days(self):
        self.client.force_login(self.person.role)
        res = self.client.post(
            "/api/evenements/creer/",
            data={
                **self.valid_data,
                "endTime": self.start_time + timezone.timedelta(days=8),
            },
        )
        self.assertEqual(res.status_code, 422)
        self.assertIn("endTime", res.data)

    def test_event_is_not_created_with_missing_contact(self):
        self.client.force_login(self.person.role)
        res = self.client.post(
            "/api/evenements/creer/", data={**self.valid_data, "contact": None}
        )
        self.assertEqual(res.status_code, 422)
        self.assertIn("contact", res.data)

    def test_event_is_not_created_with_missing_contact_property(self):
        self.client.force_login(self.person.role)
        res = self.client.post(
            "/api/evenements/creer/", data={**self.valid_data, "contact": {}}
        )
        self.assertEqual(res.status_code, 422)
        self.assertIn("contact", res.data)
        self.assertIn("name", res.data["contact"])
        self.assertIn("email", res.data["contact"])
        self.assertIn("phone", res.data["contact"])

    def test_event_is_not_created_with_missing_location(self):
        self.client.force_login(self.person.role)
        res = self.client.post(
            "/api/evenements/creer/", data={**self.valid_data, "location": None}
        )
        self.assertEqual(res.status_code, 422)
        self.assertIn("location", res.data)

    def test_event_is_not_created_with_missing_location_property(self):
        self.client.force_login(self.person.role)
        res = self.client.post(
            "/api/evenements/creer/", data={**self.valid_data, "location": {}}
        )
        self.assertEqual(res.status_code, 422)
        self.assertIn("location", res.data)
        self.assertIn("name", res.data["location"])
        self.assertIn("address1", res.data["location"])
        self.assertIn("zip", res.data["location"])
        self.assertIn("city", res.data["location"])
        self.assertIn("country", res.data["location"])

    def test_event_is_not_created_with_missing_subtype(self):
        self.client.force_login(self.person.role)
        res = self.client.post(
            "/api/evenements/creer/", data={**self.valid_data, "subtype": None}
        )
        self.assertEqual(res.status_code, 422)
        self.assertIn("subtype", res.data)

    def test_event_is_not_created_with_unmanaged_organizer_group(self):
        self.client.force_login(self.person.role)
        res = self.client.post(
            "/api/evenements/creer/",
            data={**self.valid_data, "organizerGroup": str(self.unmanaged_group.pk)},
        )
        self.assertEqual(res.status_code, 422)
        self.assertIn("organizerGroup", res.data)

    def test_event_is_not_created_with_invalid_onlineUrl(self):
        self.client.force_login(self.person.role)
        res = self.client.post(
            "/api/evenements/creer/",
            data={**self.valid_data, "onlineUrl": "not an URL!"},
        )
        self.assertEqual(res.status_code, 422)
        self.assertIn("onlineUrl", res.data)


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
        self.assertEqual(res.status_code, 401)

    def test_2022_person_can_rsvp_insoumise_event(self):
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
        self.assertEqual(res.status_code, 201)

    def test_insoumise_person_can_rsvp_2022_event(self):
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
        self.assertEqual(res.status_code, 201)

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
        self.assertEqual(res.status_code, 405)
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
        self.assertEqual(res.status_code, 405)
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
        self.assertEqual(res.status_code, 405)
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

    def test_rsvp_is_created_upon_rsvping(self):
        event = Event.objects.create(
            name="Event", start_time=self.start_time, end_time=self.end_time,
        )
        self.client.force_login(self.person.role)
        self.assertFalse(RSVP.objects.filter(event=event, person=self.person,).exists())
        res = self.client.post(f"/api/evenements/{event.pk}/inscription/")
        self.assertEqual(res.status_code, 201)
        self.assertTrue(RSVP.objects.filter(event=event, person=self.person,).exists())


class QuitEventAPITestCase(APITestCase):
    def setUp(self):
        self.person = Person.objects.create(
            email="person@example.com", create_role=True,
        )
        self.start_time = timezone.now() + timezone.timedelta(hours=2)
        self.end_time = self.start_time + timezone.timedelta(hours=2)

    def test_anonymous_person_cannot_quit(self):
        self.client.logout()
        event = Event.objects.create(
            name="Event", start_time=self.start_time, end_time=self.end_time
        )
        res = self.client.delete(f"/api/evenements/{event.pk}/inscription/")
        self.assertEqual(res.status_code, 401)

    def test_person_cannot_quit_past_event(self):
        event = Event.objects.create(
            name="Event",
            start_time=self.start_time - timezone.timedelta(days=2),
            end_time=self.end_time - timezone.timedelta(days=2),
        )
        rsvp = RSVP.objects.create(event=event, person=self.person)
        self.client.force_login(self.person.role)
        res = self.client.delete(f"/api/evenements/{event.pk}/inscription/")
        self.assertEqual(res.status_code, 404)

    def test_person_cannot_quit_if_not_participant(self):
        event = Event.objects.create(
            name="Event", start_time=self.start_time, end_time=self.end_time,
        )
        other_person = Person.objects.create(
            email="other_person@example.com", create_role=True,
        )
        rsvp = RSVP.objects.create(event=event, person=other_person)
        self.client.force_login(self.person.role)
        res = self.client.delete(f"/api/evenements/{event.pk}/inscription/")
        self.assertEqual(res.status_code, 404)

    def test_person_can_quit_future_rsvped_event(self):
        event = Event.objects.create(
            name="Event", start_time=self.start_time, end_time=self.end_time,
        )
        rsvp = RSVP.objects.create(event=event, person=self.person)
        self.assertTrue(RSVP.objects.filter(event=event, person=self.person,).exists())
        self.client.force_login(self.person.role)
        res = self.client.delete(f"/api/evenements/{event.pk}/inscription/")
        self.assertEqual(res.status_code, 204)
        self.assertFalse(RSVP.objects.filter(event=event, person=self.person,).exists())
