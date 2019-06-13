from django.test import TestCase, RequestFactory
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework.reverse import reverse as rf_reverse

from agir.notifications.actions import get_notifications
from agir.notifications.models import Notification, NotificationStatus
from agir.people.models import Person


class NotificationsTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_person("test@test.com")
        self.client.force_login(self.person.role)

    def test_can_follow_notification(self):
        notification = Notification.objects.create(
            content="Test", link="https://lafranceinsoumise.fr"
        )

        res = self.client.get(notification.get_absolute_url())

        self.assertRedirects(
            res, "https://lafranceinsoumise.fr", fetch_redirect_response=False
        )

        self.assert_(notification.statuses.filter(person=self.person).exists())
        self.assertEqual(
            NotificationStatus.STATUS_CLICKED,
            notification.statuses.get(person=self.person).status,
        )

    def test_can_mark_as_seen(self):
        for i in range(3):
            Notification.objects.create(
                id=i, content=str(i), link="https://lafranceinsoumise.fr"
            )

        client = APIClient()
        client.force_authenticate(self.person.role)
        res = client.post(
            rf_reverse("notifications_seen"), data={"notifications": [0, 2]}
        )
        self.assertEqual(res.status_code, 200)

        self.assertTrue(
            NotificationStatus.objects.filter(
                notification_id=0,
                person=self.person,
                status=NotificationStatus.STATUS_SEEN,
            ).exists()
        )
        self.assertFalse(
            NotificationStatus.objects.filter(
                notification_id=1,
                person=self.person,
                status=NotificationStatus.STATUS_SEEN,
            ).exists()
        )
        self.assertTrue(
            NotificationStatus.objects.filter(
                notification_id=2,
                person=self.person,
                status=NotificationStatus.STATUS_SEEN,
            ).exists()
        )

    def test_mark_as_seen_wont_change_clicked_notification(self):
        n = Notification.objects.create(
            id=0, content="content", link="https://lafranceinsoumise.fr"
        )

        NotificationStatus.objects.create(
            notification=n, person=self.person, status=NotificationStatus.STATUS_CLICKED
        )

        res = self.client.post(
            reverse("notifications_seen"), data={"notifications": [0]}
        )
        self.assertEqual(res.status_code, 200)

        self.assertTrue(
            n.statuses.filter(
                person=self.person, status=NotificationStatus.STATUS_CLICKED
            ).exists()
        )

    def test_appropriate_notifications_are_shown(self):
        self.maxDiff = None
        for i in range(4):
            Notification.objects.create(
                id=i, content="content", link="https://lafranceinsoumise.fr"
            )

        NotificationStatus.objects.create(
            notification_id=1,
            person=self.person,
            status=NotificationStatus.STATUS_CLICKED,
        )
        NotificationStatus.objects.create(
            notification_id=3, person=self.person, status=NotificationStatus.STATUS_SEEN
        )

        request = RequestFactory().get("/")
        request.user = self.person.role

        notifications = get_notifications(request)

        expected = [
            {
                "id": i,
                "content": "content",
                "link": "https://lafranceinsoumise.fr",
                "icon": "envelope",
                "status": "U",
            }
            for i in range(4)
        ]
        expected[1]["status"] = NotificationStatus.STATUS_CLICKED
        expected[3]["status"] = NotificationStatus.STATUS_SEEN

        self.assertEqual(notifications, list(reversed(expected)))
