import tempfile
import uuid
from unittest import skip
from unittest.mock import patch

from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from agir.event_requests.models import EventAsset
from agir.events.models import Event, EventSubtype, GroupAttendee, OrganizerConfig, RSVP
from agir.events.serializers import EventProjectSerializer
from agir.gestion.models import Projet
from agir.gestion.typologies import TypeProjet
from agir.groups.models import SupportGroup, Membership
from agir.lib.tests.mixins import create_location
from agir.msgs.models import SupportGroupMessage
from agir.payments.models import Payment
from agir.people.models import Person, PersonForm, PersonFormSubmission


class CreateEventAPITestCase(APITestCase):
    def setUp(self):
        self.geocode_element = patch("agir.events.tasks.geocode_element", autospec=True)
        self.geocode_element.start()
        self.addCleanup(self.geocode_element.stop)

        self.is_forbidden_during_treve_event = patch(
            "agir.events.serializers.is_forbidden_during_treve_event",
            return_value=False,
        )
        self.is_forbidden_during_treve_event.start()
        self.addCleanup(self.is_forbidden_during_treve_event.stop)

        self.managed_group = SupportGroup.objects.create()
        self.unmanaged_group = SupportGroup.objects.create()
        self.person = Person.objects.create_person(
            email="person@example.com",
            create_role=True,
        )
        Membership.objects.create(
            supportgroup=self.managed_group,
            person=self.person,
            membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )
        self.start_time = timezone.now() + timezone.timedelta(days=3)
        self.end_time = timezone.now() + timezone.timedelta(days=3, hours=4)
        self.location = create_location()
        self.subtype = EventSubtype.objects.create(
            visibility=EventSubtype.VISIBILITY_ALL, label=uuid.uuid4().hex
        )
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
            "subtype": self.subtype.id,
            "organizerGroup": self.managed_group.id,
            "legal": "{}",
            "onlineUrl": "https://visio.lafranceinsoumise.fr/abcdef",
        }

    def test_wrong_timezone_raise_correct_exception(self):
        self.client.force_login(self.person.role)
        form_with_wrong_timezone = {**self.valid_data, "timezone": "Africa/Porto+Novo"}
        res = self.client.post("/api/evenements/creer/", data=form_with_wrong_timezone)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(res.data["timezone"][0], "TimeZone inconnue")

    def test_anonymous_person_cannot_post(self):
        self.client.logout()
        res = self.client.post("/api/evenements/creer/", data=self.valid_data)
        self.assertEqual(res.status_code, 401)

    def test_authenticated_user_can_post(self):
        self.client.force_login(self.person.role)
        res = self.client.post("/api/evenements/creer/", data=self.valid_data)
        self.assertEqual(res.status_code, 201, res.data)

    def test_event_is_created_upon_posting_valid_data(self):
        self.client.force_login(self.person.role)
        initial_event_length = Event.objects.all().count()
        res = self.client.post("/api/evenements/creer/", data=self.valid_data)
        self.assertEqual(res.status_code, 201, res.data)
        self.assertIn("id", res.data)
        self.assertEqual(Event.objects.all().count(), initial_event_length + 1)

    def test_organizer_config_is_created_upon_posting_valid_data_with_managed_group(
        self,
    ):
        self.client.force_login(self.person.role)
        res = self.client.post("/api/evenements/creer/", data=self.valid_data)
        self.assertEqual(res.status_code, 201, res.data)
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
        self.assertEqual(res.status_code, 201, res.data)
        self.assertIn("id", res.data)
        organizer_config = OrganizerConfig.objects.filter(
            event_id=res.data["id"],
            as_group=None,
            person=self.person,
        )
        self.assertEqual(organizer_config.count(), 1)

    def test_rsvp_is_created_upon_posting_valid_data(self):
        self.client.force_login(self.person.role)
        res = self.client.post("/api/evenements/creer/", data=self.valid_data)
        self.assertEqual(res.status_code, 201, res.data)
        self.assertIn("id", res.data)
        rsvp = OrganizerConfig.objects.filter(
            event_id=res.data["id"],
            person=self.person,
        )
        self.assertEqual(rsvp.count(), 1)

    @patch("agir.events.tasks.send_event_creation_notification.delay")
    def test_event_creation_notification_task_is_created_upon_posting_valid_data(
        self, send_event_creation_notification
    ):
        send_event_creation_notification.assert_not_called()
        self.client.force_login(self.person.role)
        res = self.client.post("/api/evenements/creer/", data=self.valid_data)
        self.assertEqual(res.status_code, 201, res.data)
        self.assertIn("id", res.data)
        send_event_creation_notification.assert_called_once()

    @patch("agir.events.tasks.geocode_event.delay")
    def test_geocoding_task_is_created_upon_posting_valid_data(self, geocode_event):
        geocode_event.assert_not_called()
        self.client.force_login(self.person.role)
        res = self.client.post("/api/evenements/creer/", data=self.valid_data)
        self.assertEqual(res.status_code, 201, res.data)
        self.assertIn("id", res.data)
        geocode_event.assert_called_once()

    @patch("agir.groups.tasks.notify_new_group_event.delay")
    def test_notify_new_group_event_task_is_created_upon_posting_valid_data_with_organizer_group(
        self, notify_new_group_event
    ):
        notify_new_group_event.assert_not_called()
        self.client.force_login(self.person.role)
        res = self.client.post("/api/evenements/creer/", data=self.valid_data)
        self.assertEqual(res.status_code, 201, res.data)
        self.assertIn("id", res.data)
        notify_new_group_event.assert_called_once()

    @patch("agir.groups.tasks.send_new_group_event_email.delay")
    def test_send_new_group_event_email_task_is_created_upon_posting_valid_data_with_organizer_group(
        self, send_new_group_event_email
    ):
        send_new_group_event_email.assert_not_called()
        self.client.force_login(self.person.role)
        res = self.client.post("/api/evenements/creer/", data=self.valid_data)
        self.assertEqual(res.status_code, 201, res.data)
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
        self.assertEqual(res.status_code, 201, res.data)
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
        self.assertEqual(res.status_code, 201, res.data)
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

    @skip("This code is commented out except during national elections")
    @patch("agir.lib.geo.geocode_france")
    def test_gestion_projet_is_created_for_related_new_event_subtype(
        self, geocode_france
    ):
        self.client.force_login(self.person.role)

        subtype_without_related_project_type = EventSubtype.objects.create(
            label="2017!",
            related_project_type="",
            visibility=EventSubtype.VISIBILITY_ALL,
        )
        res = self.client.post(
            "/api/evenements/creer/",
            data={
                **self.valid_data,
                "subtype": subtype_without_related_project_type.id,
            },
        )
        self.assertEqual(res.status_code, 201)
        new_event_id = res.data["id"]
        self.assertFalse(Projet.objects.filter(event_id=new_event_id).exists())

        subtype_with_related_project_type = EventSubtype.objects.create(
            label="2022!",
            related_project_type=TypeProjet.DEBATS,
            visibility=EventSubtype.VISIBILITY_ALL,
        )
        res = self.client.post(
            "/api/evenements/creer/",
            data={
                **self.valid_data,
                "subtype": subtype_with_related_project_type.id,
            },
        )
        self.assertEqual(res.status_code, 201)
        new_event_id = res.data["id"]
        self.assertTrue(Projet.objects.filter(event_id=new_event_id).exists())

    @patch("agir.events.serializers.is_forbidden_during_treve_event", return_value=True)
    def test_event_with_forbidden_during_treve_data(
        self, is_forbidden_during_treve_event
    ):
        self.client.force_login(self.person.role)
        res = self.client.post(
            "/api/evenements/creer/",
            data={**self.valid_data},
        )
        self.assertEqual(res.status_code, 422)
        self.assertIn("endTime", res.data)

    def test_for_organizer_group_members_only_subtype_event_is_not_created_without_organizer_group(
        self,
    ):
        subtype = EventSubtype.objects.create(
            visibility=EventSubtype.VISIBILITY_ALL,
            label=uuid.uuid4().hex,
            for_organizer_group_members_only=True,
        )
        self.client.force_login(self.person.role)
        res = self.client.post(
            "/api/evenements/creer/",
            data={**self.valid_data, "subtype": subtype.id, "organizerGroup": None},
        )
        self.assertEqual(res.status_code, 422)
        self.assertIn("organizerGroup", res.data)

    def test_for_supportgroup_type_subtype_event_is_not_created_without_organizer_group(
        self,
    ):
        subtype = EventSubtype.objects.create(
            visibility=EventSubtype.VISIBILITY_ALL,
            label=uuid.uuid4().hex,
            for_supportgroup_type=SupportGroup.TYPE_LOCAL_GROUP,
        )
        self.client.force_login(self.person.role)
        res = self.client.post(
            "/api/evenements/creer/",
            data={**self.valid_data, "subtype": subtype.id, "organizerGroup": None},
        )
        self.assertEqual(res.status_code, 422)
        self.assertIn("organizerGroup", res.data)

    def test_for_supportgroup_type_subtype_event_is_not_created_for_different_type_group(
        self,
    ):
        local_group = SupportGroup.objects.create(type=SupportGroup.TYPE_LOCAL_GROUP)
        thematic_group = SupportGroup.objects.create(type=SupportGroup.TYPE_THEMATIC)
        Membership.objects.create(
            supportgroup=local_group,
            person=self.person,
            membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )
        Membership.objects.create(
            supportgroup=thematic_group,
            person=self.person,
            membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )
        subtype = EventSubtype.objects.create(
            visibility=EventSubtype.VISIBILITY_ALL,
            label=uuid.uuid4().hex,
            for_supportgroup_type=SupportGroup.TYPE_LOCAL_GROUP,
        )
        self.client.force_login(self.person.role)
        res = self.client.post(
            "/api/evenements/creer/",
            data={
                **self.valid_data,
                "subtype": subtype.id,
                "organizerGroup": str(thematic_group.id),
            },
        )
        self.assertEqual(res.status_code, 422)
        self.assertIn("organizerGroup", res.data)
        res = self.client.post(
            "/api/evenements/creer/",
            data={
                **self.valid_data,
                "subtype": subtype.id,
                "organizerGroup": str(local_group.id),
            },
        )
        self.assertEqual(res.status_code, 201, res.data)

    def test_for_supportgroups_subtype_event_is_not_created_without_organizer_group(
        self,
    ):
        authorized_group = SupportGroup.objects.create()
        subtype = EventSubtype.objects.create(
            visibility=EventSubtype.VISIBILITY_ALL, label=uuid.uuid4().hex
        )
        subtype.for_supportgroups.add(authorized_group)
        self.client.force_login(self.person.role)
        res = self.client.post(
            "/api/evenements/creer/",
            data={**self.valid_data, "subtype": subtype.id, "organizerGroup": None},
        )
        self.assertEqual(res.status_code, 422)
        self.assertIn("organizerGroup", res.data)

    def test_for_supportgroups_subtype_event_is_not_created_for_different_type_group(
        self,
    ):
        authorized_group = SupportGroup.objects.create()
        unauthorized_group = SupportGroup.objects.create()
        Membership.objects.create(
            supportgroup=authorized_group,
            person=self.person,
            membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )
        Membership.objects.create(
            supportgroup=unauthorized_group,
            person=self.person,
            membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )
        subtype = EventSubtype.objects.create(
            visibility=EventSubtype.VISIBILITY_ALL, label=uuid.uuid4().hex
        )
        subtype.for_supportgroups.add(authorized_group)
        self.client.force_login(self.person.role)
        res = self.client.post(
            "/api/evenements/creer/",
            data={
                **self.valid_data,
                "subtype": subtype.id,
                "organizerGroup": str(unauthorized_group.id),
            },
        )
        self.assertEqual(res.status_code, 422)
        self.assertIn("organizerGroup", res.data)
        res = self.client.post(
            "/api/evenements/creer/",
            data={
                **self.valid_data,
                "subtype": subtype.id,
                "organizerGroup": str(authorized_group.id),
            },
        )
        self.assertEqual(res.status_code, 201, res.data)


class RSVPEventAPITestCase(APITestCase):
    def setUp(self):
        self.person = Person.objects.create_person(
            email="person@example.com", create_role=True, is_political_support=True
        )
        self.organizer = Person.objects.create_person(
            email="organizer@example.com", create_role=True, is_political_support=True
        )
        self.start_time = timezone.now()
        self.end_time = self.start_time + timezone.timedelta(hours=2)

    def create_event(self, **kwargs):
        defaults = {
            "name": "Event",
            "start_time": self.start_time,
            "end_time": self.end_time,
            "organizer_person": self.organizer,
        }
        kwargs = {**defaults, **kwargs}
        return Event.objects.create(**kwargs)

    def test_anonymous_person_cannot_rsvp(self):
        self.client.logout()
        event = self.create_event()
        res = self.client.post(f"/api/evenements/{event.pk}/inscription/")
        self.assertEqual(res.status_code, 401)

    def test_person_cannot_rsvp_event_with_subscription_form(self):
        subscription_form = PersonForm.objects.create()
        event = self.create_event(
            subscription_form_id=subscription_form.pk,
        )
        self.client.force_login(self.person.role)
        res = self.client.post(f"/api/evenements/{event.pk}/inscription/")
        self.assertEqual(res.status_code, 403)
        self.assertIn("redirectTo", res.data)

    def test_person_cannot_rsvp_if_already_participant(self):
        event = self.create_event()
        RSVP.objects.create(
            event=event,
            person=self.person,
            status=RSVP.Status.CONFIRMED,
        )
        self.client.force_login(self.person.role)
        res = self.client.post(f"/api/evenements/{event.pk}/inscription/")
        self.assertEqual(res.status_code, 403)
        self.assertIn("redirectTo", res.data)

    def test_person_cannot_rsvp_if_event_is_not_free(self):
        event = self.create_event(
            payment_parameters='{"price":10}',
        )
        RSVP.objects.create(
            event=event,
            person=self.person,
            status=RSVP.Status.CONFIRMED,
        )
        self.client.force_login(self.person.role)
        res = self.client.post(f"/api/evenements/{event.pk}/inscription/")
        self.assertEqual(res.status_code, 403)
        self.assertIn("redirectTo", res.data)

    def test_person_can_rsvp_for_organizer_group_members_only_if_person_is_group_member(
        self,
    ):
        subtype = EventSubtype.objects.create(
            visibility=EventSubtype.VISIBILITY_ALL, label=uuid.uuid4().hex
        )
        subtype.for_organizer_group_members_only = True
        subtype.save()
        group = SupportGroup.objects.create(name="Group")
        event = self.create_event(
            subtype=subtype,
            organizer_group=group,
        )
        RSVP.objects.create(
            event=event,
            person=self.person,
            status=RSVP.Status.CONFIRMED,
        )
        self.client.force_login(self.person.role)
        res = self.client.post(f"/api/evenements/{event.pk}/inscription/")
        self.assertEqual(res.status_code, 403)
        member = Person.objects.create_person("member@agir.test", create_role=True)
        Membership.objects.create(
            supportgroup=group,
            person=member,
            membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
        )
        self.client.force_login(member.role)
        res = self.client.post(f"/api/evenements/{event.pk}/inscription/")
        self.assertEqual(res.status_code, 201, res.data)

    def test_authenticated_person_can_rsvp_available_event(self):
        event = self.create_event()
        self.client.force_login(self.person.role)
        res = self.client.post(f"/api/evenements/{event.pk}/inscription/")
        self.assertEqual(res.status_code, 201, res.data)

    @patch("agir.events.views.api_views.rsvp_to_free_event")
    def test_rsvp_to_free_event_is_called_upon_joining(self, rsvp_to_free_event):
        event = self.create_event()
        self.client.force_login(self.person.role)
        rsvp_to_free_event.assert_not_called()
        res = self.client.post(f"/api/evenements/{event.pk}/inscription/")
        self.assertEqual(res.status_code, 201, res.data)
        rsvp_to_free_event.assert_called()

    def test_rsvp_is_created_upon_rsvping(self):
        event = self.create_event()
        self.client.force_login(self.person.role)
        self.assertFalse(
            RSVP.objects.confirmed()
            .filter(
                event=event,
                person=self.person,
            )
            .exists()
        )
        res = self.client.post(f"/api/evenements/{event.pk}/inscription/")
        self.assertEqual(res.status_code, 201, res.data)
        self.assertTrue(
            RSVP.objects.confirmed()
            .filter(
                event=event,
                person=self.person,
            )
            .exists()
        )


class RSVPEventAsGroupAPITestCase(APITestCase):
    def setUp(self):
        self.person = Person.objects.create_person(
            email="person@example.com", create_role=True, is_political_support=True
        )
        self.start_time = timezone.now()
        self.end_time = self.start_time + timezone.timedelta(hours=2)

    def test_person_cannot_rsvp_for_group_without_permission(self):
        group = SupportGroup.objects.create()
        event = Event.objects.create(
            name="Event", start_time=self.start_time, end_time=self.end_time
        )
        member = Person.objects.create_person(
            email="member@agir.local", create_role=True
        )
        Membership.objects.create(
            supportgroup=group,
            person=member,
            membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
        )

        self.client.force_login(member.role)
        res = self.client.post(
            f"/api/evenements/{event.pk}/inscription-groupe/{group.pk}/"
        )
        self.assertEqual(res.status_code, 403)

    def test_cannot_rsvp_for_organizer_group_members_only_event_as_group(self):
        subtype = EventSubtype.objects.create(
            visibility=EventSubtype.VISIBILITY_ALL, label=uuid.uuid4().hex
        )
        subtype.for_organizer_group_members_only = True
        subtype.save()
        group = SupportGroup.objects.create()
        event = Event.objects.create(
            name="Event",
            start_time=self.start_time,
            end_time=self.end_time,
            subtype=subtype,
        )
        member = Person.objects.create_person(
            email="member@agir.local", create_role=True
        )
        Membership.objects.create(
            supportgroup=group,
            person=member,
            membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )

        self.client.force_login(member.role)
        res = self.client.post(
            f"/api/evenements/{event.pk}/inscription-groupe/{group.pk}/"
        )
        self.assertEqual(res.status_code, 403)

    def test_person_can_rsvp_as_a_group(self):
        group = SupportGroup.objects.create()
        event = Event.objects.create(
            name="Event", start_time=self.start_time, end_time=self.end_time
        )
        referent = Person.objects.create_person(
            email="referent@agir.local", create_role=True
        )
        Membership.objects.create(
            supportgroup=group,
            person=referent,
            membership_type=Membership.MEMBERSHIP_TYPE_REFERENT,
        )
        self.client.force_login(referent.role)
        res = self.client.post(
            f"/api/evenements/{event.pk}/inscription-groupe/{group.pk}/"
        )
        self.assertEqual(res.status_code, 201, res.data)

    def test_person_cannot_quit_event_as_group_without_permission(self):
        group = SupportGroup.objects.create()
        event = Event.objects.create(
            name="Event", start_time=self.start_time, end_time=self.end_time
        )
        member = Person.objects.create_person(
            email="member@agir.local", create_role=True
        )
        Membership.objects.create(
            supportgroup=group,
            person=member,
            membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
        )
        referent = Person.objects.create_person(
            email="referent@agir.local", create_role=True
        )
        Membership.objects.create(
            supportgroup=group,
            person=referent,
            membership_type=Membership.MEMBERSHIP_TYPE_REFERENT,
        )
        GroupAttendee.objects.create(group=group, event=event, organizer=referent)

        self.client.force_login(member.role)
        res = self.client.delete(
            f"/api/evenements/{event.pk}/inscription-groupe/{group.pk}/"
        )
        self.assertEqual(res.status_code, 403)

    def test_person_can_quit_event_as_group(self):
        group = SupportGroup.objects.create()
        event = Event.objects.create(
            name="Event", start_time=self.start_time, end_time=self.end_time
        )
        referent = Person.objects.create_person(
            email="referent@agir.local", create_role=True
        )
        Membership.objects.create(
            supportgroup=group,
            person=referent,
            membership_type=Membership.MEMBERSHIP_TYPE_REFERENT,
        )
        GroupAttendee.objects.create(group=group, event=event, organizer=referent)

        self.client.force_login(referent.role)
        res = self.client.delete(
            f"/api/evenements/{event.pk}/inscription-groupe/{group.pk}/"
        )
        self.assertEqual(res.status_code, 204)


class QuitEventAPITestCase(APITestCase):
    def setUp(self):
        self.person = Person.objects.create_person(
            email="person@example.com",
            create_role=True,
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
        self.assertEqual(res.status_code, 403)

    def test_person_cannot_quit_paid_event(self):
        event = Event.objects.create(
            name="Event",
            start_time=self.start_time - timezone.timedelta(days=2),
            end_time=self.end_time - timezone.timedelta(days=2),
        )
        rsvp = RSVP.objects.create(
            event=event, person=self.person, status=RSVP.Status.CONFIRMED
        )
        rsvp.payment = Payment.objects.create(
            status=Payment.STATUS_COMPLETED,
            price=100,
            type="evenement",
            mode="check_events",
        )
        rsvp.save()
        self.client.force_login(self.person.role)
        res = self.client.delete(f"/api/evenements/{event.pk}/inscription/")
        self.assertEqual(res.status_code, 403)

    def test_person_can_quit_if_not_participant(self):
        event = Event.objects.create(
            name="Event",
            start_time=self.start_time,
            end_time=self.end_time,
        )
        other_person = Person.objects.create_person(
            email="other_person@example.com",
            create_role=True,
        )
        RSVP.objects.create(event=event, person=other_person)
        self.client.force_login(self.person.role)
        res = self.client.delete(f"/api/evenements/{event.pk}/inscription/")
        self.assertEqual(res.status_code, 204)
        self.assertTrue(
            RSVP.objects.filter(
                event=event, person=self.person, status=RSVP.Status.CANCELLED
            )
        )

    def test_person_can_quit_if_waiting_payment(self):
        event = Event.objects.create(
            name="Event",
            start_time=self.start_time,
            end_time=self.end_time,
        )
        rsvp = RSVP.objects.create(
            event=event, person=self.person, status=RSVP.Status.AWAITING_PAYMENT
        )
        rsvp.payment = Payment.objects.create(
            status=Payment.STATUS_WAITING,
            price=100,
            type="evenement",
            mode="check_events",
        )
        rsvp.save()
        self.client.force_login(rsvp.person.role)
        res = self.client.delete(f"/api/evenements/{event.pk}/inscription/")
        self.assertEqual(res.status_code, 204)
        rsvp.refresh_from_db(fields=("status",))
        rsvp.payment.refresh_from_db(fields=("status",))
        self.assertEqual(rsvp.status, RSVP.Status.CANCELLED)
        self.assertEqual(rsvp.payment.status, Payment.STATUS_CANCELED)

    def test_person_can_quit_future_rsvped_event(self):
        event = Event.objects.create(
            name="Event",
            start_time=self.start_time,
            end_time=self.end_time,
        )
        rsvp = RSVP.objects.create(event=event, person=self.person)
        self.assertEqual(rsvp.status, RSVP.Status.CONFIRMED)
        self.client.force_login(self.person.role)
        res = self.client.delete(f"/api/evenements/{event.pk}/inscription/")
        self.assertEqual(res.status_code, 204)
        rsvp.refresh_from_db()
        self.assertEqual(rsvp.status, RSVP.Status.CANCELLED)


class UpdateEventAPITestCase(APITestCase):
    def setUp(self):
        self.is_forbidden_during_treve_event = patch(
            "agir.events.serializers.is_forbidden_during_treve_event",
            return_value=False,
        )
        self.is_forbidden_during_treve_event.start()
        self.addCleanup(self.is_forbidden_during_treve_event.stop)

        self.unrelated_person = Person.objects.create_person(
            email="unrelated_person@example.com",
            create_role=True,
        )
        self.organizer = Person.objects.create_person(
            email="organizer@example.com",
            create_role=True,
        )
        start_time = timezone.now() + timezone.timedelta(days=3)
        end_time = timezone.now() + timezone.timedelta(days=3, hours=4)
        self.a_subtype = EventSubtype.objects.create(
            visibility=EventSubtype.VISIBILITY_ALL, label="A subtype"
        )
        self.another_subtype = EventSubtype.objects.create(
            visibility=EventSubtype.VISIBILITY_ALL, label="Another subtype"
        )
        self.event = Event.objects.create(
            name="Event",
            start_time=start_time,
            end_time=end_time,
            timezone=timezone.get_default_timezone_name(),
            subtype=self.a_subtype,
            organizer_person=self.organizer,
        )
        self.past_event = Event.objects.create(
            name="Event",
            start_time=timezone.now() - timezone.timedelta(days=3),
            end_time=timezone.now() - timezone.timedelta(days=2),
            timezone=timezone.get_default_timezone_name(),
            subtype=self.a_subtype,
            organizer_person=self.organizer,
        )

    def test_anonymous_person_cannot_update(self):
        self.client.logout()
        data = {"subtype": self.another_subtype.pk}
        res = self.client.patch(f"/api/evenements/{self.event.pk}/modifier/", data=data)
        self.assertEqual(res.status_code, 401)

    def test_non_organizer_cannot_update(self):
        self.client.force_login(self.unrelated_person.role)
        data = {"subtype": self.another_subtype.pk}
        res = self.client.patch(f"/api/evenements/{self.event.pk}/modifier/", data=data)
        self.assertEqual(res.status_code, 403)

    def test_organizer_cannot_post_non_public_subtype(self):
        self.client.force_login(self.organizer.role)
        hidden_subtype = EventSubtype.objects.create(
            visibility=EventSubtype.VISIBILITY_NONE, label="Hidden subtype"
        )
        data = {"subtype": hidden_subtype.pk}
        res = self.client.patch(f"/api/evenements/{self.event.pk}/modifier/", data=data)
        self.assertEqual(res.status_code, 422)
        self.assertIn("subtype", res.data)

    def test_organizer_can_post_valid_subtype(self):
        self.client.force_login(self.organizer.role)
        data = {"subtype": self.another_subtype.pk}
        res = self.client.patch(f"/api/evenements/{self.event.pk}/modifier/", data=data)
        self.assertEqual(res.status_code, 200)
        self.assertIn("subtype", res.data)
        self.assertEqual(res.data["subtype"], data["subtype"])

    def test_can_update_event_only_for_upcoming_events(self):
        self.client.force_login(self.organizer.role)
        data = {"name": "ABC"}

        res = self.client.patch(
            f"/api/evenements/{self.past_event.pk}/modifier/", data=data
        )
        self.assertEqual(res.status_code, 422)
        self.assertIn("name", res.data)

        res = self.client.patch(f"/api/evenements/{self.event.pk}/modifier/", data=data)
        self.assertEqual(res.status_code, 200)
        self.assertIn("name", res.data)
        self.assertEqual(res.data["name"], data["name"])

    @patch("agir.events.serializers.is_forbidden_during_treve_event", return_value=True)
    def test_event_with_forbidden_during_treve_data(
        self, is_forbidden_during_treve_event
    ):
        self.client.force_login(self.organizer.role)
        data = {"subtype": self.another_subtype.pk}
        res = self.client.patch(f"/api/evenements/{self.event.pk}/modifier/", data=data)
        self.assertEqual(res.status_code, 422)
        self.assertIn("global", res.data)


class EventProjectAPITestCase(APITestCase):
    def setUp(self):
        self.unrelated_person = Person.objects.create_person(
            email="unrelated_person@example.com",
            create_role=True,
        )
        self.organizer = Person.objects.create_person(
            email="organizer@example.com",
            create_role=True,
        )
        start_time = timezone.now() + timezone.timedelta(days=3)
        end_time = timezone.now() + timezone.timedelta(days=3, hours=4)
        self.a_subtype = EventSubtype.objects.create(
            visibility=EventSubtype.VISIBILITY_ALL,
            label="A subtype",
            type=EventSubtype.TYPE_PUBLIC_ACTION,
        )
        self.event = Event.objects.create(
            name="Event",
            start_time=start_time,
            end_time=end_time,
            timezone=timezone.get_default_timezone_name(),
            subtype=self.a_subtype,
            organizer_person=self.organizer,
        )
        self.project = Projet.objects.create(
            titre="Project", type=TypeProjet.choices[0][0], event=self.event
        )
        self.event_wo_project = Event.objects.create(
            name="Event without project",
            start_time=start_time,
            end_time=end_time,
            timezone=timezone.get_default_timezone_name(),
            subtype=self.a_subtype,
            organizer_person=self.organizer,
        )
        self.valid_update_data = {
            "dismissedDocumentTypes": [
                EventProjectSerializer.Meta.valid_document_types[0]
            ]
        }

    ## GET
    def test_anonymous_person_cannot_retrieve_project(self):
        self.client.logout()
        res = self.client.get(f"/api/evenements/{self.event.pk}/projet/")
        self.assertEqual(res.status_code, 401)

    def test_non_organizer_person_cannot_retrieve_project(self):
        self.client.force_login(self.unrelated_person.role)
        res = self.client.get(f"/api/evenements/{self.event.pk}/projet/")
        self.assertEqual(res.status_code, 403)

    def test_organizer_person_cannot_retrieve_project_if_none_exists(self):
        self.client.force_login(self.organizer.role)
        res = self.client.get(f"/api/evenements/{self.event_wo_project.pk}/projet/")
        self.assertEqual(res.status_code, 404)

    def test_organizer_person_can_retrieve_project_if_one_exists(self):
        self.client.force_login(self.organizer.role)
        res = self.client.get(f"/api/evenements/{self.event.pk}/projet/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["projectId"], self.project.pk)

    ## PATCH
    def test_anonymous_person_cannot_update_project(self):
        self.client.logout()
        res = self.client.patch(
            f"/api/evenements/{self.event.pk}/projet/", data=self.valid_update_data
        )
        self.assertEqual(res.status_code, 401)

    def test_non_organizer_person_cannot_update_project(self):
        self.client.force_login(self.unrelated_person.role)
        res = self.client.patch(
            f"/api/evenements/{self.event.pk}/projet/", data=self.valid_update_data
        )
        self.assertEqual(res.status_code, 403)

    def test_organizer_person_cannot_update_project_if_none_exists(self):
        self.client.force_login(self.organizer.role)
        res = self.client.patch(
            f"/api/evenements/{self.event_wo_project.pk}/projet/",
            data=self.valid_update_data,
        )
        self.assertEqual(res.status_code, 404)

    def test_organizer_person_cannot_update_with_invalid_data(self):
        self.client.force_login(self.organizer.role)
        data = {"dismissedDocumentTypes": None}
        res = self.client.patch(
            f"/api/evenements/{self.event.pk}/projet/",
            data=data,
        )
        self.assertEqual(res.status_code, 422)

        data = {
            "dismissedDocumentTypes": [
                "NOT-" + EventProjectSerializer.Meta.valid_document_types[0]
            ]
        }
        res = self.client.patch(
            f"/api/evenements/{self.event.pk}/projet/",
            data=data,
        )
        self.assertEqual(res.status_code, 422)

    def test_organizer_person_can_update_project_if_one_exists(self):
        self.client.force_login(self.organizer.role)
        res = self.client.patch(
            f"/api/evenements/{self.event.pk}/projet/", data=self.valid_update_data
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["projectId"], self.project.pk)
        self.assertEqual(
            res.data["dismissedDocumentTypes"],
            self.valid_update_data["dismissedDocumentTypes"],
        )

    def test_updating_dismissed_document_types_does_not_override_instance_details(self):
        self.client.force_login(self.organizer.role)
        self.project.details = {"a": "a", "documents": {"b": "b"}}
        self.project.save()
        res = self.client.patch(
            f"/api/evenements/{self.event.pk}/projet/", data=self.valid_update_data
        )
        self.assertEqual(res.status_code, 200)
        self.project.refresh_from_db()
        self.assertEqual(
            self.project.details,
            {
                "a": "a",
                "documents": {
                    "b": "b",
                    "absent": self.valid_update_data["dismissedDocumentTypes"],
                },
            },
        )


class CreateEventProjectDocumentAPITestCase(APITestCase):
    def setUp(self):
        self.unrelated_person = Person.objects.create_person(
            email="unrelated_person@example.com",
            create_role=True,
        )
        self.organizer = Person.objects.create_person(
            email="organizer@example.com",
            create_role=True,
        )
        start_time = timezone.now() + timezone.timedelta(days=3)
        end_time = timezone.now() + timezone.timedelta(days=3, hours=4)
        self.a_subtype = EventSubtype.objects.create(
            visibility=EventSubtype.VISIBILITY_ALL,
            label="A subtype",
            type=EventSubtype.TYPE_PUBLIC_ACTION,
        )
        self.event = Event.objects.create(
            name="Event",
            start_time=start_time,
            end_time=end_time,
            timezone=timezone.get_default_timezone_name(),
            subtype=self.a_subtype,
            organizer_person=self.organizer,
        )
        self.project = Projet.objects.create(
            titre="Project", type=TypeProjet.choices[0][0], event=self.event
        )
        self.event_wo_project = Event.objects.create(
            name="Event without project",
            start_time=start_time,
            end_time=end_time,
            timezone=timezone.get_default_timezone_name(),
            subtype=self.a_subtype,
            organizer_person=self.organizer,
        )

        image = Image.new("RGB", (100, 100))
        tmp_file = tempfile.NamedTemporaryFile(suffix=".jpg")
        image.save(tmp_file)
        tmp_file.seek(0)

        self.valid_data = {
            "type": EventProjectSerializer.Meta.valid_document_types[0],
            "name": "A document",
            "description": "A description",
            "file": tmp_file,
        }

    def test_anonymous_person_cannot_add_document(self):
        self.client.logout()
        res = self.client.post(
            f"/api/evenements/{self.event.pk}/projet/document/",
            data=self.valid_data,
            format="multipart",
        )
        self.assertEqual(res.status_code, 401)

    def test_non_organizer_person_cannot_add_document(self):
        self.client.force_login(self.unrelated_person.role)
        res = self.client.post(
            f"/api/evenements/{self.event.pk}/projet/document/",
            data=self.valid_data,
            format="multipart",
        )
        self.assertEqual(res.status_code, 403)

    def test_organizer_person_cannot_add_document_if_project_does_not_exists(self):
        self.client.force_login(self.organizer.role)
        res = self.client.post(
            f"/api/evenements/{self.event_wo_project.pk}/projet/document/",
            data=self.valid_data,
            format="multipart",
        )
        self.assertEqual(res.status_code, 404)

    def test_organizer_person_cannot_add_document_if_type_is_invalid(self):
        self.client.force_login(self.organizer.role)
        data = {**self.valid_data, "type": "Not a valid type"}
        res = self.client.post(
            f"/api/evenements/{self.event.pk}/projet/document/",
            data=data,
            format="multipart",
        )
        self.assertEqual(res.status_code, 422)
        self.assertIn("type", res.data)

    def test_organizer_person_cannot_add_document_if_name_is_invalid(self):
        self.client.force_login(self.organizer.role)
        data = {**self.valid_data, "name": ""}
        res = self.client.post(
            f"/api/evenements/{self.event.pk}/projet/document/",
            data=data,
            format="multipart",
        )
        self.assertEqual(res.status_code, 422)
        self.assertIn("name", res.data)

    def test_organizer_person_cannot_add_document_if_file_is_invalid(self):
        self.client.force_login(self.organizer.role)
        data = {**self.valid_data, "file": ""}
        res = self.client.post(
            f"/api/evenements/{self.event.pk}/projet/document/",
            data=data,
            format="multipart",
        )
        self.assertEqual(res.status_code, 422)
        self.assertIn("file", res.data)

    def test_organizer_person_can_add_document_if_project_exists_and_data_is_valid(
        self,
    ):
        original_document_length = self.project.documents.count()
        self.client.force_login(self.organizer.role)
        res = self.client.post(
            f"/api/evenements/{self.event.pk}/projet/document/",
            data=self.valid_data,
            format="multipart",
        )
        self.assertEqual(res.status_code, 201, res.data)
        self.project.refresh_from_db()
        self.assertEqual(self.project.documents.count(), original_document_length + 1)


class EventProjectsAPITestCase(APITestCase):
    def setUp(self):
        self.unrelated_person = Person.objects.create_person(
            email="unrelated_person@example.com",
            create_role=True,
        )
        self.organizer = Person.objects.create_person(
            email="organizer@example.com",
            create_role=True,
        )
        start_time = timezone.now() + timezone.timedelta(days=3)
        end_time = timezone.now() + timezone.timedelta(days=3, hours=4)
        self.a_subtype = EventSubtype.objects.create(
            visibility=EventSubtype.VISIBILITY_ALL,
            label="A subtype",
            type=EventSubtype.TYPE_PUBLIC_ACTION,
        )
        self.event = Event.objects.create(
            name="Event",
            start_time=start_time,
            end_time=end_time,
            timezone=timezone.get_default_timezone_name(),
            subtype=self.a_subtype,
            organizer_person=self.organizer,
        )
        self.project = Projet.objects.create(
            titre="Project", type=TypeProjet.choices[0][0], event=self.event
        )

    def test_anonymous_person_cannot_retrieve_projects(self):
        self.client.logout()
        res = self.client.get(f"/api/evenements/projets/")
        self.assertEqual(res.status_code, 401)

    def test_non_organizer_person_can_retrieve_no_project(self):
        self.client.force_login(self.unrelated_person.role)
        res = self.client.get(f"/api/evenements/projets/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 0)

    def test_organizer_person_can_retrieve_projects(self):
        self.client.force_login(self.organizer.role)
        res = self.client.get(f"/api/evenements/projets/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)


class EventReportPersonFormAPITestCase(APITestCase):
    def setUp(self):
        self.unrelated_person = Person.objects.create(
            email="unrelated_person@example.com",
            create_role=True,
        )
        self.organizer = Person.objects.create(
            email="organizer@example.com",
            create_role=True,
        )
        self.report_person_form = PersonForm.objects.create(
            title="Form", description="Form", slug="formulaire"
        )
        self.subtype_with_form = EventSubtype.objects.create(
            visibility=EventSubtype.VISIBILITY_ALL,
            label="Subtype with form",
            report_person_form=self.report_person_form,
        )
        self.subtype_without_form = EventSubtype.objects.create(
            visibility=EventSubtype.VISIBILITY_ALL,
            label="Subtype without form",
            report_person_form=None,
        )
        self.event_without_form = Event.objects.create(
            name="Event",
            start_time=timezone.now() + timezone.timedelta(days=3),
            end_time=timezone.now() + timezone.timedelta(days=3, hours=4),
            timezone=timezone.get_default_timezone_name(),
            subtype=self.subtype_without_form,
            organizer_person=self.organizer,
        )
        self.upcomint_event = Event.objects.create(
            name="Upcoming",
            start_time=timezone.now() + timezone.timedelta(days=3),
            end_time=timezone.now() + timezone.timedelta(days=3, hours=4),
            timezone=timezone.get_default_timezone_name(),
            subtype=self.subtype_with_form,
            organizer_person=self.organizer,
        )
        self.past_event = Event.objects.create(
            name="Past",
            start_time=timezone.now() - timezone.timedelta(days=3),
            end_time=timezone.now() - timezone.timedelta(days=2),
            timezone=timezone.get_default_timezone_name(),
            subtype=self.subtype_with_form,
            organizer_person=self.organizer,
        )
        self.too_old_event = Event.objects.create(
            name="Too old",
            start_time=timezone.now() - timezone.timedelta(days=9),
            end_time=timezone.now() - timezone.timedelta(days=8),
            timezone=timezone.get_default_timezone_name(),
            subtype=self.subtype_with_form,
            organizer_person=self.organizer,
        )

    def test_anonymous_person_cannot_retrieve_form(self):
        self.client.logout()
        res = self.client.get(f"/api/evenements/{self.past_event.pk}/bilan/")
        self.assertEqual(res.status_code, 401)

    def test_non_organizer_cannot_retrieve_form(self):
        self.client.force_login(self.unrelated_person.role)
        res = self.client.get(f"/api/evenements/{self.past_event.pk}/bilan/")
        self.assertEqual(res.status_code, 403)

    def test_cannot_retrieve_form_for_unexisting_event(self):
        self.client.force_login(self.organizer.role)
        res = self.client.get(f"/api/evenements/{uuid.uuid4()}/bilan/")
        self.assertEqual(res.status_code, 404)

    def test_cannot_retrieve_form_for_event_with_formless_subtype(self):
        self.client.force_login(self.organizer.role)
        res = self.client.get(f"/api/evenements/{self.event_without_form.pk}/bilan/")
        self.assertEqual(res.status_code, 404)

    def test_can_retrieve_form_for_more_than_a_week_old_event(self):
        self.client.force_login(self.organizer.role)
        res = self.client.get(f"/api/evenements/{self.too_old_event.pk}/bilan/")
        self.assertEqual(res.status_code, 404)

    def test_can_retrieve_form_for_upcoming_event(self):
        self.client.force_login(self.organizer.role)
        res = self.client.get(f"/api/evenements/{self.upcomint_event.pk}/bilan/")
        self.assertEqual(res.status_code, 200)

    def test_organizer_can_retrieve_form_for_less_than_a_week_old_event(self):
        self.client.force_login(self.organizer.role)
        res = self.client.get(f"/api/evenements/{self.past_event.pk}/bilan/")
        self.assertEqual(res.status_code, 200)

    def test_organizer_can_retrieve_form_url_with_event_query_param(self):
        self.client.force_login(self.organizer.role)
        res = self.client.get(f"/api/evenements/{self.past_event.pk}/bilan/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("url", res.data)
        self.assertIn(
            f"/formulaires/formulaire/?reported_event_id={self.past_event.pk}",
            res.data["url"],
        )

    def test_organizer_can_retrieve_form_submission_state_for_event(self):
        self.client.force_login(self.organizer.role)
        res = self.client.get(f"/api/evenements/{self.past_event.pk}/bilan/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("submitted", res.data)
        self.assertFalse(res.data["submitted"])

        PersonFormSubmission.objects.create(
            form=self.report_person_form,
            person=self.organizer,
            data={"reported_event_id": str(self.upcomint_event.pk)},
        )
        res = self.client.get(f"/api/evenements/{self.past_event.pk}/bilan/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("submitted", res.data)
        self.assertFalse(res.data["submitted"])

        PersonFormSubmission.objects.create(
            form=self.report_person_form,
            person=self.organizer,
            data={"reported_event_id": str(self.past_event.pk)},
        )
        res = self.client.get(f"/api/evenements/{self.past_event.pk}/bilan/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("submitted", res.data)
        self.assertTrue(res.data["submitted"])


class EventTestMessageAPITestCase(APITestCase):
    def setUp(self):
        self.organizer = Person.objects.create_person(
            email="organizer@example.com",
            create_role=True,
        )
        start_time = timezone.now() + timezone.timedelta(days=3)
        end_time = timezone.now() + timezone.timedelta(days=3, hours=4)
        self.event = Event.objects.create(
            name="Event",
            start_time=start_time,
            end_time=end_time,
            organizer_person=self.organizer,
        )

        self.group = SupportGroup.objects.create(name="Groupe 1")
        self.group2 = SupportGroup.objects.create(name="Groupe 2")
        self.referent = Person.objects.create_person(
            email="referent@example.com",
            create_role=True,
        )
        Membership.objects.create(
            supportgroup=self.group,
            person=self.referent,
            membership_type=Membership.MEMBERSHIP_TYPE_REFERENT,
        )
        self.member = Person.objects.create_person(
            email="member@example.com",
            create_role=True,
        )
        Membership.objects.create(
            supportgroup=self.group,
            person=self.member,
            membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
        )

        # 3 messages on event : 2 from group1 with different permission, 1 from group2
        SupportGroupMessage.objects.create(
            supportgroup=self.group,
            author=self.referent,
            text="Lorem",
            linked_event=self.event,
        )
        SupportGroupMessage.objects.create(
            supportgroup=self.group,
            author=self.referent,
            text="Lorem",
            required_membership_type=Membership.MEMBERSHIP_TYPE_REFERENT,
            linked_event=self.event,
        )
        self.other_message = SupportGroupMessage.objects.create(
            supportgroup=self.group2,
            author=self.referent,
            text="Lorem",
            linked_event=self.event,
        )

    def test_members_can_get_own_group_messages(self):
        self.client.force_login(self.member.role)
        res = self.client.get(f"/api/evenements/{self.event.pk}/messages/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)

    def test_referent_can_get_own_group_messages(self):
        self.client.force_login(self.referent.role)
        res = self.client.get(f"/api/evenements/{self.event.pk}/messages/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 3)

    def test_members_cannot_get_others_group_messages(self):
        self.client.force_login(self.member.role)
        res = self.client.get(f"/api/evenements/{self.event.pk}/messages/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["id"] == self.other_message.pk, False)


class EventAssetListAPITestCase(APITestCase):
    def setUp(self):
        self.unrelated_person = Person.objects.create_person(
            email="unrelated_person@example.com",
            create_role=True,
        )
        self.organizer = Person.objects.create_person(
            email="organizer@example.com",
            create_role=True,
        )
        start_time = timezone.now() + timezone.timedelta(days=3)
        end_time = timezone.now() + timezone.timedelta(days=3, hours=4)
        self.a_subtype = EventSubtype.objects.create(
            visibility=EventSubtype.VISIBILITY_ALL,
            label="A subtype",
            type=EventSubtype.TYPE_PUBLIC_ACTION,
        )
        self.event = Event.objects.create(
            name="Event",
            start_time=start_time,
            end_time=end_time,
            timezone=timezone.get_default_timezone_name(),
            subtype=self.a_subtype,
            organizer_person=self.organizer,
        )
        self.published_event_asset = EventAsset.objects.create(
            name="published asset",
            file=SimpleUploadedFile(
                "document.png",
                b"Un faux fichier",
                content_type="image/png",
            ),
            event=self.event,
            published=True,
        )
        self.unpublished_event_asset = EventAsset.objects.create(
            name="published asset",
            file=SimpleUploadedFile(
                "document.png",
                b"Un faux fichier",
                content_type="image/png",
            ),
            event=self.event,
            published=False,
        )

    def get_url(self, event):
        return reverse("api_event_assets", args=(event.pk,))

    def test_anonymous_person_cannot_retrieve_asset(self):
        self.client.logout()
        res = self.client.get(self.get_url(self.event))
        self.assertEqual(res.status_code, 401)

    def test_non_organizer_person_cannot_retrieve_asset(self):
        self.client.force_login(self.unrelated_person.role)
        res = self.client.get(self.get_url(self.event))
        self.assertEqual(res.status_code, 403)

    def test_organizer_person_cannot_retrieve_asset_if_event_does_not_exist(self):
        self.client.force_login(self.organizer.role)
        res = self.client.get(self.get_url(Event()))
        self.assertEqual(res.status_code, 404)

    def test_organizer_person_can_retrieve_assets(self):
        self.client.force_login(self.organizer.role)
        res = self.client.get(self.get_url(self.event))
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.data, list)

    def test_organizer_person_can_retrieve_only_published_assets(self):
        self.client.force_login(self.organizer.role)
        res = self.client.get(self.get_url(self.event))
        self.assertEqual(res.status_code, 200)
        self.assertIn(str(self.published_event_asset.id), [a["id"] for a in res.data])
        self.assertNotIn(
            str(self.unpublished_event_asset.id), [a["id"] for a in res.data]
        )


class EventListAPITestCase(APITestCase):
    def setUp(self):
        self.person = Person.objects.create_person(
            email="person@agir.test",
            create_role=True,
        )
        self.unavailable_attendee = Person.objects.create_person(
            email="unavailable@agir.test",
            create_role=True,
        )
        self.attendee = Person.objects.create_person(
            email="attendee@agir.test",
            create_role=True,
        )
        self.creator = Person.objects.create_person(
            email="creator@agir.test",
            create_role=True,
        )
        self.organizer = Person.objects.create_person(
            email="organizer@agir.test",
            create_role=True,
        )
        self.attending_group = SupportGroup.objects.create(name="a")
        self.attending_group_manager = Person.objects.create_person(
            email="a_manager@agir.test",
            create_role=True,
        )
        Membership.objects.create(
            supportgroup=self.attending_group,
            person=self.attending_group_manager,
            membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )
        self.organizing_group = SupportGroup.objects.create(name="o")
        self.organizing_group_manager = Person.objects.create_person(
            email="o_manager@agir.test",
            create_role=True,
        )
        Membership.objects.create(
            supportgroup=self.organizing_group,
            person=self.organizing_group_manager,
            membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )
        start_time = timezone.now() + timezone.timedelta(days=3)
        end_time = timezone.now() + timezone.timedelta(days=3, hours=4)
        self.event = Event.objects.create(
            name="Event",
            start_time=start_time,
            end_time=end_time,
            timezone=timezone.get_default_timezone_name(),
            organizer_person=self.creator,
        )
        RSVP.objects.create(
            event=self.event,
            person=self.unavailable_attendee,
            status=RSVP.Status.CANCELLED,
        )
        RSVP.objects.create(
            event=self.event, person=self.attendee, status=RSVP.Status.CONFIRMED
        )
        OrganizerConfig.objects.create(
            event=self.event,
            person=self.organizer,
        )
        GroupAttendee.objects.create(
            event=self.event,
            group=self.attending_group,
            organizer=self.attending_group_manager,
        )
        OrganizerConfig.objects.create(
            event=self.event,
            person=self.organizing_group_manager,
            as_group=self.organizing_group,
        )

    def make_request(self, endpoint, person):
        self.client.force_login(person.role)
        return self.client.get(endpoint)

    def test_event_rsvped_api_view(self):
        endpoint = "/api/evenements/rsvped/"
        expected = {
            self.person: 0,
            self.unavailable_attendee: 0,
            self.attendee: 1,
            # Creator is automatically added as organizer and attendee
            self.creator: 1,
            self.organizer: 0,
            self.attending_group_manager: 0,
            self.organizing_group_manager: 0,
        }
        for person, expected_length in expected.items():
            res = self.make_request(endpoint, person)
            self.assertEqual(res.status_code, 200)
            self.assertEqual(len(res.data), expected_length)

    def test_past_event_api_view(self):
        endpoint = "/api/evenements/rsvped/passes/"
        expected = {
            self.person: 0,
            self.unavailable_attendee: 0,
            self.attendee: 0,
            self.creator: 0,
            self.organizer: 0,
            self.attending_group_manager: 0,
            self.organizing_group_manager: 0,
        }
        for person, expected_length in expected.items():
            res = self.make_request(endpoint, person)
            self.assertEqual(res.status_code, 200)
            self.assertEqual(len(res.data), expected_length, person)

        self.event.start_time = timezone.now() - timezone.timedelta(days=3)
        self.event.end_time = timezone.now() - timezone.timedelta(days=3, hours=4)
        self.event.save()

        expected = {
            self.person: 0,
            self.unavailable_attendee: 0,
            self.attendee: 1,
            self.creator: 1,
            self.organizer: 0,
            self.attending_group_manager: 0,
            self.organizing_group_manager: 0,
        }
        for person, expected_length in expected.items():
            res = self.make_request(endpoint, person)
            self.assertEqual(res.status_code, 200)
            self.assertEqual(len(res.data), expected_length)

    def test_ongoing_event_api_view(self):
        endpoint = "/api/evenements/rsvped/en-cours/"
        expected = {
            self.person: 0,
            self.unavailable_attendee: 0,
            self.attendee: 0,
            self.creator: 0,
            self.organizer: 0,
            self.attending_group_manager: 0,
            self.organizing_group_manager: 0,
        }
        for person, expected_length in expected.items():
            res = self.make_request(endpoint, person)
            self.assertEqual(res.status_code, 200)
            self.assertEqual(len(res.data), expected_length, person)

        self.event.start_time = timezone.now() - timezone.timedelta(days=3)
        self.event.end_time = timezone.now() + timezone.timedelta(days=3, hours=4)
        self.event.save()

        expected = {
            self.person: 0,
            self.unavailable_attendee: 0,
            self.attendee: 1,
            self.creator: 1,
            self.organizer: 0,
            self.attending_group_manager: 0,
            self.organizing_group_manager: 0,
        }
        for person, expected_length in expected.items():
            res = self.make_request(endpoint, person)
            self.assertEqual(res.status_code, 200)
            self.assertEqual(len(res.data), expected_length)

    def test_user_group_event_api_view(self):
        endpoint = "/api/evenements/mes-groupes/"
        expected = {
            self.person: 0,
            self.unavailable_attendee: 0,
            self.attendee: 0,
            self.creator: 0,
            self.organizer: 0,
            self.attending_group_manager: 1,
            self.organizing_group_manager: 1,
        }
        for person, expected_length in expected.items():
            res = self.make_request(endpoint, person)
            self.assertEqual(res.status_code, 200)
            self.assertEqual(len(res.data), expected_length, person)

    def test_user_organized_event_api_view(self):
        endpoint = "/api/evenements/organises/"
        expected = {
            self.person: 0,
            self.unavailable_attendee: 0,
            self.attendee: 0,
            self.creator: 1,
            self.organizer: 1,
            self.attending_group_manager: 0,
            self.organizing_group_manager: 1,
        }
        for person, expected_length in expected.items():
            res = self.make_request(endpoint, person)
            self.assertEqual(res.status_code, 200)
            self.assertEqual(len(res.data), expected_length, person)

    def test_event_suggestion_api_view(self):
        endpoint = "/api/evenements/suggestions/"
        expected = {
            self.person: 0,
            self.unavailable_attendee: 0,
            self.attendee: 0,
            self.creator: 0,
            self.organizer: 0,
            self.attending_group_manager: 1,
            self.organizing_group_manager: 1,
        }
        for person, expected_length in expected.items():
            res = self.make_request(endpoint, person)
            self.assertEqual(res.status_code, 200)
            self.assertEqual(len(res.data), expected_length, person)


class EventDetailViewTestCase(APITestCase):
    def setUp(self):
        self.organizer = Person.objects.create_person(
            email="organizer@agir.test",
            create_role=True,
        )
        self.organizer_group = SupportGroup.objects.create(name="Organizer Group")
        self.organizer_group_manager = Person.objects.create_person(
            email="organizer_group_manager@agir.test",
            create_role=True,
        )
        self.organizer_group.memberships.create(
            person=self.organizer_group_manager,
            membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )
        self.organizer_group_active_member = Person.objects.create_person(
            email="organizer_group_active_member@agir.test",
            create_role=True,
        )
        self.organizer_group.memberships.create(
            person=self.organizer_group_active_member,
            membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
        )
        self.organizer_group_follower = Person.objects.create_person(
            email="organizer_group_follower@agir.test",
            create_role=True,
        )
        self.organizer_group.memberships.create(
            person=self.organizer_group_follower,
            membership_type=Membership.MEMBERSHIP_TYPE_FOLLOWER,
        )
        self.confirmed_rsvp = Person.objects.create_person(
            email="confirmed_rsvp@agir.test",
            create_role=True,
        )
        self.cancelled_rsvp = Person.objects.create_person(
            email="cancelled_rsvp@agir.test",
            create_role=True,
        )
        self.start_time = timezone.now() + timezone.timedelta(hours=2)
        self.end_time = self.start_time + timezone.timedelta(hours=2)
        self.event = Event.objects.create_event(
            name="Event",
            start_time=self.start_time,
            end_time=self.end_time,
            organizer_person=self.organizer,
            organizer_group=self.organizer_group,
            report_content="<p>This is a report</p>",
        )
        self.event.rsvps.create(
            person=self.confirmed_rsvp, status=RSVP.Status.CONFIRMED
        )
        self.event.rsvps.create(
            person=self.cancelled_rsvp, status=RSVP.Status.CANCELLED
        )

    def test_only_organizers_rsvps_and_organizing_group_members_can_view_report(self):
        self.client.logout()
        response = self.client.get(f"/api/evenements/{self.event.pk}/details/")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("report", response.data)

        unauthorized_person = Person.objects.create_person(
            "unauthorized_person@agir.test", create_role=True
        )
        self.client.force_login(unauthorized_person.role)
        response = self.client.get(f"/api/evenements/{self.event.pk}/details/")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("report", response.data)

        self.client.force_login(self.organizer_group_follower.role)
        response = self.client.get(f"/api/evenements/{self.event.pk}/details/")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("report", response.data)

        self.client.force_login(self.cancelled_rsvp.role)
        response = self.client.get(f"/api/evenements/{self.event.pk}/details/")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("report", response.data)

        for user in [
            "organizer",
            "organizer_group_manager",
            "organizer_group_active_member",
            "confirmed_rsvp",
        ]:
            person = getattr(self, user)
            self.client.force_login(person.role)
            response = self.client.get(f"/api/evenements/{self.event.pk}/details/")
            self.assertEqual(response.status_code, 200)
            self.assertIn("report", response.data)
            self.assertEqual(
                response.data["report"]["content"], self.event.report_content
            )
