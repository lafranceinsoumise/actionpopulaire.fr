from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from agir.activity.models import Activity
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
