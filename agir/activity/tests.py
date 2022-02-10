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
        res = self.client.get("/api/user/activities/")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("results", res.data)
        self.assertEqual(len(res.data["results"]), 1)

    def test_cannot_view_own_activity_if_cannot_view_linked_event(self):
        event = Event.objects.create(
            name="Evenement test",
            visibility=Event.VISIBILITY_ADMIN,
            start_time=now(),
            end_time=now() + timedelta(minutes=30),
        )
        self.own_activity.event = event
        self.own_activity.save()

        res = self.client.get("/api/user/activities/")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("results", res.data)
        self.assertEqual(len(res.data["results"]), 0)


class AnnouncementTestCase(TestCase):
    def setUp(self) -> None:
        self.insoumise = Person.objects.create_insoumise("a@a.a")

        self.nsp = Person.objects.create_person("b@b.b", is_2022=True)

    def test_can_get_all_announcements(self):
        a1 = Announcement.objects.create(
            title="1ère annonce",
            link="https://lafranceinsoumise.fr",
            content="SUPER",
        )

        a2 = Announcement.objects.create(
            title="2ème annonce", link="https://melenchon2022.fr", content="GO SIGNEZ"
        )

        announcements = get_announcements(self.insoumise)
        self.assertCountEqual(announcements, [a2, a1])

    def test_can_limit_announcement_with_segment(self):
        segment_insoumis = Segment.objects.create(
            is_insoumise=True, is_2022=None, newsletters=[]
        )
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

    def test_activity_is_created_if_none_exists_for_authenticated_person(self):
        announcement = Announcement.objects.create(
            title="1ère annonce",
            link="https://lafranceinsoumise.fr",
            content="SUPER",
        )
        self.assertFalse(
            Activity.objects.filter(
                announcement=announcement, recipient=self.insoumise
            ).exists()
        )
        get_announcements(self.insoumise)
        self.assertTrue(
            Activity.objects.filter(
                announcement=announcement, recipient=self.insoumise
            ).exists()
        )

    def test_activity_is_not_created_if_one_exists_for_the_authenticated_person(self):
        announcement = Announcement.objects.create(
            title="1ère annonce",
            link="https://lafranceinsoumise.fr",
            content="SUPER",
        )
        Activity.objects.create(
            announcement=announcement,
            recipient=self.insoumise,
            type=Activity.TYPE_ANNOUNCEMENT,
        )
        self.assertEqual(
            Activity.objects.filter(
                announcement=announcement, recipient=self.insoumise
            ).count(),
            1,
        )
        get_announcements(self.insoumise)
        self.assertEqual(
            Activity.objects.filter(
                announcement=announcement, recipient=self.insoumise
            ).count(),
            1,
        )


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
            self.p1.activities.filter(status=Activity.STATUS_DISPLAYED),
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
            self.p1.activities.filter(status=Activity.STATUS_INTERACTED),
            [self.a1, self.a2],
        )

    def test_cannot_update_someone_else_activity(self):
        self.client.force_login(self.p1.role)
        res = self.client.post(
            "/api/activity/bulk/update-status/",
            data={
                "status": Activity.STATUS_INTERACTED,
                "ids": [self.a3.id],
            },
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
            data={
                "status": Activity.STATUS_DISPLAYED,
                "ids": [self.a1.id],
            },
        )
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        self.a1.refresh_from_db()
        self.assertEqual(
            self.a1.status,
            Activity.STATUS_INTERACTED,
            "le champ `status' n'aurait pas dû changer !",
        )


class AnnouncementAPITestCase(TestCase):
    def setUp(self) -> None:
        self.person = Person.objects.create_insoumise(email="a@a.a", create_role=True)
        self.non_custom_announcement = Announcement.objects.create(
            title="Non Custom Announcement",
            link="https://lafranceinsoumise.fr",
            content="SUPER",
            custom_display="",
        )
        self.custom_announcement = Announcement.objects.create(
            title="Custom Announcement",
            link="https://lafranceinsoumise.fr",
            content="SUPER",
            custom_display="custom",
        )

    def test_unauthenticated_user_get_only_non_custom_announcements(self):
        self.client.logout()
        response = self.client.get("/api/announcements/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], str(self.non_custom_announcement.id))
        self.assertIsNone(response.data[0]["activityId"])

    def test_authenticated_user_get_only_non_custom_announcements(self):
        self.client.force_login(self.person.role)
        response = self.client.get("/api/announcements/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], str(self.non_custom_announcement.id))
        self.assertIsNotNone(response.data[0]["activityId"])

    def test_announcement_activity_is_not_automatically_set_as_displayed_for_authenticated_user(
        self,
    ):
        self.client.force_login(self.person.role)
        activity = Activity.objects.create(
            recipient=self.person,
            announcement=self.non_custom_announcement,
            type=Activity.TYPE_ANNOUNCEMENT,
            status=Activity.STATUS_UNDISPLAYED,
        )
        response = self.client.get("/api/announcements/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], str(self.non_custom_announcement.id))
        self.assertEqual(activity.pk, response.data[0]["activityId"])
        activity.refresh_from_db()
        self.assertEqual(activity.status, Activity.STATUS_UNDISPLAYED)

    def test_announcement_activity_is_automatically_set_as_displayed_if_mark_as_displayed_params_is_set_to_1(
        self,
    ):
        self.client.force_login(self.person.role)
        activity = Activity.objects.create(
            recipient=self.person,
            announcement=self.non_custom_announcement,
            type=Activity.TYPE_ANNOUNCEMENT,
            status=Activity.STATUS_UNDISPLAYED,
        )
        response = self.client.get("/api/announcements/?mark_as_displayed=1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], str(self.non_custom_announcement.id))
        self.assertEqual(activity.pk, response.data[0]["activityId"])
        activity.refresh_from_db()
        self.assertEqual(activity.status, Activity.STATUS_DISPLAYED)


class UserCustomAnnouncementAPITestCase(TestCase):
    def setUp(self) -> None:
        self.person = Person.objects.create_insoumise(email="a@a.a", create_role=True)
        self.custom_announcement = Announcement.objects.create(
            title="Custom Announcement",
            link="https://lafranceinsoumise.fr",
            content="SUPER",
            custom_display="custom",
        )

    def test_unauthenticated_user_cannot_get_custom_announcements(self):
        self.client.logout()
        response = self.client.get(
            f"/api/user/announcements/custom/{self.custom_announcement.custom_display}/"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_get_a_custom_announcement(self):
        self.client.force_login(self.person.role)
        response = self.client.get(
            f"/api/user/announcements/custom/{self.custom_announcement.custom_display}/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.custom_announcement.id))
        self.assertIsNotNone(response.data["activityId"])

    def test_announcement_activity_is_automatically_set_as_displayed_for_authenticated_user(
        self,
    ):
        self.client.force_login(self.person.role)
        activity = Activity.objects.create(
            recipient=self.person,
            announcement=self.custom_announcement,
            type=Activity.TYPE_ANNOUNCEMENT,
            status=Activity.STATUS_UNDISPLAYED,
        )
        response = self.client.get(
            f"/api/user/announcements/custom/{self.custom_announcement.custom_display}/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.custom_announcement.id))
        self.assertEqual(activity.pk, response.data["activityId"])
        activity.refresh_from_db()
        self.assertEqual(activity.status, Activity.STATUS_DISPLAYED)

    def test_authenticated_user_can_get_a_custom_announcement_if_activity_status_is_interacted(
        self,
    ):
        self.client.force_login(self.person.role)
        Activity.objects.create(
            recipient=self.person,
            announcement=self.custom_announcement,
            type=Activity.TYPE_ANNOUNCEMENT,
            status=Activity.STATUS_INTERACTED,
        )
        response = self.client.get(
            f"/api/user/announcements/custom/{self.custom_announcement.custom_display}/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.custom_announcement.id))
