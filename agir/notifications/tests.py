from unittest.mock import Mock

from django.test import TestCase
from django.urls import reverse
from rest_framework.reverse import reverse as rf_reverse
from rest_framework.test import APIClient

from agir.notifications.actions import get_notifications
from agir.notifications.models import Announcement, Notification
from agir.people.models import Person


class NotificationsTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_person("test@test.com", create_role=True)
        self.client.force_login(self.person.role)

    def test_can_follow_notification(self):
        notification = Notification.objects.create(
            content="Test", link="https://lafranceinsoumise.fr", person=self.person
        )

        res = self.client.get(notification.get_absolute_url())

        self.assertRedirects(
            res, "https://lafranceinsoumise.fr", fetch_redirect_response=False
        )

        notification.refresh_from_db()
        self.assertEqual(notification.status, Notification.STATUS_CLICKED)

    def test_notification_is_created_from_announcement(self):
        Announcement.objects.create(content="Test", link="https://lafranceinsoumise.fr")

        request = Mock()
        request.user = self.person.role

        user_notifications = get_notifications(request)

        self.assertEqual(len(user_notifications), 1)

        self.assertEqual(user_notifications[0]["content"], "Test")
        self.assertEqual(user_notifications[0]["link"], "https://lafranceinsoumise.fr")

        self.assert_(
            Notification.objects.filter(pk=user_notifications[0]["id"]).exists()
        )

    def test_can_mark_as_seen(self):
        notifs = [
            Notification.objects.create(
                id=i,
                content=str(i),
                link="https://lafranceinsoumise.fr",
                person=self.person,
            )
            for i in range(3)
        ]

        client = APIClient()
        client.force_authenticate(self.person.role)

        request = Mock()
        request.user = self.person.role

        res = client.post(
            rf_reverse("notifications_seen"), data={"notifications": [0, 2]}
        )
        self.assertEqual(res.status_code, 200)

        for n in notifs:
            n.refresh_from_db()

        self.assertEqual(
            [n.status for n in notifs],
            [
                Notification.STATUS_SEEN,
                Notification.STATUS_UNDISPLAYED,
                Notification.STATUS_SEEN,
            ],
        )

    def test_mark_as_seen_wont_change_clicked_notification(self):
        a = Announcement.objects.create(
            id=0, content="content", link="https://lafranceinsoumise.fr"
        )

        n = Notification.objects.create(
            announcement=a, person=self.person, status=Notification.STATUS_CLICKED
        )

        res = self.client.post(
            reverse("notifications_seen"), data={"notifications": [n.id]}
        )
        self.assertEqual(res.status_code, 200)

        self.assertTrue(
            a.notifications.filter(
                person=self.person, status=Notification.STATUS_CLICKED
            ).exists()
        )

    def test_appropriate_notifications_are_shown(self):
        self.maxDiff = None
        for i in range(4):
            Announcement.objects.create(
                id=i, content="content", link="https://lafranceinsoumise.fr"
            )

        Notification.objects.create(
            announcement_id=1, person=self.person, status=Notification.STATUS_CLICKED
        )
        Notification.objects.create(
            announcement_id=3, person=self.person, status=Notification.STATUS_SEEN
        )

        request = Mock()
        request.user = self.person.role

        notifications = get_notifications(request)

        self.assertCountEqual([n["content"] for n in notifications], ["content"] * 4)
        self.assertCountEqual(
            [n["link"] for n in notifications], ["https://lafranceinsoumise.fr"] * 4
        )
        self.assertCountEqual([n["icon"] for n in notifications], ["exclamation"] * 4)
        self.assertCountEqual(
            [n["status"] for n in notifications],
            [
                Notification.STATUS_CLICKED,
                Notification.STATUS_SEEN,
                Notification.STATUS_UNDISPLAYED,
                Notification.STATUS_UNDISPLAYED,
            ],
        )
