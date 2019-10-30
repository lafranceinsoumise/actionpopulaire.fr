from django.test import TestCase
from django.urls import reverse

from agir.lib.tests.mixins import FakeDataMixin
from agir.lib.utils import front_url
from agir.notifications.models import Notification

from ..models import OrganizerConfig, EventSubtype, Event


class SmokeTestCase(FakeDataMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.client.force_login(
            self.people["admin"].role, backend="agir.people.backend.PersonBackend"
        )

    def test_can_see_events_page(self):
        res = self.client.get(reverse("admin:events_event_changelist"))
        self.assertEqual(res.status_code, 200)

    def test_can_see_add_event_page(self):
        res = self.client.get(reverse("admin:events_event_add"))
        self.assertEqual(res.status_code, 200)

    def test_can_see_specific_event_page(self):
        res = self.client.get(
            reverse("admin:events_event_change", args=[self.events["user1_event1"].pk])
        )
        self.assertEqual(res.status_code, 200)


class AddOrganizerTestCase(FakeDataMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.client.force_login(
            self.people["admin"].role, backend="agir.people.backend.PersonBackend"
        )

    def test_can_show_add_organizer_page(self):
        res = self.client.get(
            reverse(
                "admin:events_event_add_organizer",
                args=[self.events["user1_event1"].pk],
            )
        )
        self.assertEqual(res.status_code, 200)

    def test_can_add_organizer(self):
        res = self.client.post(
            reverse(
                "admin:events_event_add_organizer",
                args=[self.events["user1_event1"].pk],
            ),
            data={"person": self.people["user2"].pk},
        )
        self.assertRedirects(
            res,
            reverse("admin:events_event_change", args=[self.events["user1_event1"].pk]),
        )
        self.assertTrue(
            OrganizerConfig.objects.filter(
                person=self.people["user2"], event=self.events["user1_event1"]
            ).exists()
        )


class DeleteNotificationTestCas(FakeDataMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.client.force_login(
            self.people["admin"].role, backend="agir.people.backend.PersonBackend"
        )
        self.notification = Notification.objects.create(
            person=self.people["admin"],
            link=front_url(
                "view_event", kwargs={"pk": self.data["events"]["user1_event1"].pk}
            ),
        )

    def test_hide_event_delete_notification(self):
        event = self.data["events"]["user1_event1"]
        event.visibility = Event.VISIBILITY_ADMIN
        event.save()

        with self.assertRaises(Notification.DoesNotExist):
            Notification.objects.get(pk=self.notification.pk)
