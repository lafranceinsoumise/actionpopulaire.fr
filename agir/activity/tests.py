from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now
from rest_framework import status

from agir.activity.actions import get_announcements
from agir.activity.models import Activity, Announcement
from agir.events.models import Event
from agir.mailing.models import Segment
from agir.people.models import Person


class ActivityAPIViewTestCase(TestCase):
    def setUp(self) -> None:
        self.person = Person.objects.create_person("a@domaine.pays", create_role=True)
        self.other_person = Person.objects.create_person("b@domain.pays")

        self.own_activity = Activity.objects.create(
            recipient=self.person, type=Activity.TYPE_GROUP_INVITATION
        )

        self.others_activity = Activity.objects.create(
            recipient=self.other_person, type=Activity.TYPE_EVENT_UPDATE
        )

        self.own_activity_url = reverse(
            "activity:api_activity", args=[self.own_activity.pk]
        )

        self.client.force_login(self.person.role)

    def test_cannot_view_or_change_activity_when_not_logged_in(self):
        self.client.logout()

        res = self.client.get(self.own_activity_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        res = self.client.put(
            self.own_activity_url,
            data={"status": Activity.STATUS_INTERACTED},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_can_view_and_change_own_activity(self):
        res = self.client.get(self.own_activity_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res = self.client.put(
            self.own_activity_url,
            data={"status": Activity.STATUS_INTERACTED},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.own_activity.refresh_from_db()
        self.assertEqual(self.own_activity.status, Activity.STATUS_INTERACTED)

    def test_cannot_view_and_change_others_activity(self):
        url = reverse("activity:api_activity", args=[self.others_activity.pk])

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        res = self.client.put(
            url,
            data={"status": Activity.STATUS_INTERACTED},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_can_list_own_activities(self):
        res = self.client.get("/api/user/required-activities/")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_cannot_view_own_activity_if_cannot_view_linked_event(self):
        event = Event.objects.create(
            name="Evenement test",
            visibility=Event.VISIBILITY_ADMIN,
            start_time=now(),
            end_time=now() + timedelta(minutes=30),
        )
        self.own_activity.event = event
        self.own_activity.save()

        res = self.client.get("/api/user/required-activities/")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 0)


class AnnouncementTestCase(TestCase):
    def setUp(self) -> None:
        self.insoumise = Person.objects.create_insoumise("a@a.a",)

        self.nsp = Person.objects.create_person("b@b.b", is_2022=True)

    def test_can_get_all_announcements(self):
        a1 = Announcement.objects.create(
            title="1ère annonce", link="https://lafranceinsoumise.fr", content="SUPER",
        )

        a2 = Announcement.objects.create(
            title="2ème annonce", link="https://noussommespour.fr", content="GO SIGNEZ"
        )

        announcements = get_announcements(self.insoumise)
        self.assertCountEqual(announcements, [a2, a1])

    def test_can_limit_announcement_with_segment(self):
        segment_insoumis = Segment.objects.create(is_insoumise=True)
        a1 = Announcement.objects.create(
            title="1ère annonce",
            link="https://lafranceinsoumise.fr",
            content="SUPER",
            segment=segment_insoumis,
        )

        announcements = get_announcements(self.insoumise)
        self.assertCountEqual(announcements, [a1])

        announcements = get_announcements(self.nsp)
        self.assertCountEqual(announcements, [])


class ActivityStatusUpdateViewTestCase(TestCase):
    def setUp(self) -> None:
        self.p1 = Person.objects.create_insoumise(email="a@a.a", create_role=True)
        self.p2 = Person.objects.create_insoumise(email="b@b.b", create_role=True)

        self.a1 = Activity.objects.create(
            recipient=self.p1, type=Activity.TYPE_GROUP_INVITATION
        )

        self.a2 = Activity.objects.create(
            recipient=self.p1, type=Activity.TYPE_GROUP_COORGANIZATION_ACCEPTED
        )

        self.a3 = Activity.objects.create(
            recipient=self.p2, type=Activity.TYPE_NEW_ATTENDEE
        )

    def test_cannot_update_status_when_unauthenticated(self):
        res = self.client.post(
            "/api/activity/bulk/update-status/",
            data={"status": Activity.STATUS_DISPLAYED, "ids": [self.a1.id]},
        )

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_can_update_own_activity(self):
        self.client.force_login(self.p1.role)
        res = self.client.post(
            "/api/activity/bulk/update-status/",
            data={"status": Activity.STATUS_DISPLAYED, "ids": [self.a1.id]},
        )
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        self.assertCountEqual(
            self.p1.received_notifications.filter(status=Activity.STATUS_DISPLAYED),
            [self.a1],
        )

    def test_can_update_multiple_activities(self):
        self.client.force_login(self.p1.role)
        res = self.client.post(
            "/api/activity/bulk/update-status/",
            data={
                "status": Activity.STATUS_INTERACTED,
                "ids": [self.a1.id, self.a2.id],
            },
        )

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        self.assertCountEqual(
            self.p1.received_notifications.filter(status=Activity.STATUS_INTERACTED),
            [self.a1, self.a2],
        )

    def test_cannot_update_someone_else_activity(self):
        self.client.force_login(self.p1.role)
        res = self.client.post(
            "/api/activity/bulk/update-status/",
            data={"status": Activity.STATUS_INTERACTED, "ids": [self.a3.id],},
        )
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        self.a3.refresh_from_db()
        self.assertEqual(self.a3.status, Activity.STATUS_UNDISPLAYED)

    def test_cannot_reduce_interaction_level(self):
        self.client.force_login(self.p1.role)
        self.a1.status = Activity.STATUS_INTERACTED
        self.a1.save()
        res = self.client.post(
            "/api/activity/bulk/update-status/",
            data={"status": Activity.STATUS_DISPLAYED, "ids": [self.a1.id],},
        )
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        self.a1.refresh_from_db()
        self.assertEqual(
            self.a1.status,
            Activity.STATUS_INTERACTED,
            "le champ `status' n'aurait pas dû changer !",
        )
