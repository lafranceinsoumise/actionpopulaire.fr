from django.utils import timezone
from rest_framework.test import APITestCase
from unittest.mock import patch

from agir.events.models import Event, EventSubtype, OrganizerConfig, RSVP
from agir.groups.models import SupportGroup, Membership
from agir.msgs.models import SupportGroupMessage, SupportGroupMessageComment
from agir.people.models import Person

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

    def test_event_is_not_created_with_missing_for_users(self):
        self.client.force_login(self.person.role)
        res = self.client.post(
            "/api/evenements/creer/", data={**self.valid_data, "forUsers": None}
        )
        self.assertEqual(res.status_code, 422)
        self.assertIn("forUsers", res.data)

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
