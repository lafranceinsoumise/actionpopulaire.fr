from django.shortcuts import reverse
from django.test import TestCase
from django.utils import timezone
from rest_framework import status

from ..events.models import Event, OrganizerConfig
from ..groups.models import SupportGroup, Membership
from ..people.models import Person


class NavbarTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_insoumise(
            "test@test.com", display_name="Arthur Machin", create_role=True
        )

        self.group = SupportGroup.objects.create(name="group")
        Membership.objects.create(
            person=self.person,
            supportgroup=self.group,
            membership_type=Membership.MEMBERSHIP_TYPE_REFERENT,
        )

    def test_session_info_authenticated(self):
        self.client.force_login(self.person.role)
        response = self.client.get("/api/session/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(b"Arthur Machin", response.content)


class PagesLoadingTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_insoumise("test@test.com", create_role=True)
        self.client.force_login(self.person.role)

        now = timezone.now()
        day = timezone.timedelta(days=1)
        hour = timezone.timedelta(hours=1)

        self.event = Event.objects.create(
            name="event", start_time=now + day, end_time=now + day + hour
        )

        OrganizerConfig.objects.create(
            event=self.event, person=self.person, is_creator=True
        )

        self.group = SupportGroup.objects.create(name="group")
        Membership.objects.create(
            person=self.person,
            supportgroup=self.group,
            membership_type=Membership.MEMBERSHIP_TYPE_REFERENT,
        )

    def test_see_event_details(self):
        response = self.client.get("/evenements/" + str(self.event.id) + "/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_see_group_details(self):
        response = self.client.get("/groupes/" + str(self.group.id) + "/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_see_create_event(self):
        response = self.client.get("/evenements/creer/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_see_create_group(self):
        person = Person.objects.create_insoumise(
            "test_group@test.com",
            create_role=True,
            first_name="Jane",
            last_name="Doe",
            gender=Person.GENDER_OTHER,
            contact_phone="+33600000000",
            contact_phone_status=Person.CONTACT_PHONE_VERIFIED,
        )
        self.client.force_login(person.role)
        response = self.client.get("/groupes/creer/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class NBUrlsTestCase(TestCase):
    def test_create_group_redirect(self):
        # new event page
        response = self.client.get("/old/users/event_pages/new?parent_id=103")

        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.url, reverse("create_event"))

    def test_unkown_gives_404(self):
        response = self.client.get("/old/nimp")

        self.assertEqual(response.status_code, 404)
