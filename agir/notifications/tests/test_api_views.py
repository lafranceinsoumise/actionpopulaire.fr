import uuid
from django.db.models import signals
from rest_framework.test import APITestCase

from agir.activity.models import Activity
from agir.groups.models import SupportGroup, Membership
from agir.notifications.models import Subscription
from agir.people.models import Person


class ListSubscriptionsAPITestCase(APITestCase):
    def setUp(self):
        signals.post_save.disconnect(
            sender=Membership, dispatch_uid="create_default_membership_subscriptions"
        )
        self.person = Person.objects.create_person(
            email="person@example.com", create_role=True
        )
        self.other_person = Person.objects.create_person(
            email="other_person@example.com", create_role=True
        )
        self.person_group = SupportGroup.objects.create()
        self.person_membership = Membership.objects.create(
            supportgroup=self.person_group,
            person=self.person,
            membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )
        self.person_subscription = Subscription.objects.create(
            person=self.person,
            type=Subscription.SUBSCRIPTION_PUSH,
            activity_type=Activity.TYPE_WAITING_LOCATION_GROUP,
            membership=self.person_membership,
        )
        self.other_person_subscription = Subscription.objects.create(
            person=self.other_person,
            type=Subscription.SUBSCRIPTION_PUSH,
            activity_type=Activity.TYPE_EVENT_UPDATE,
        )

    def test_anonymous_person_cannot_get_subscriptions(self):
        self.client.logout()
        res = self.client.get("/api/notifications/subscriptions/")
        self.assertEqual(res.status_code, 401)

    def test_authenticated_person_can_get_own_subscriptions(self):
        self.client.force_login(self.person.role)
        res = self.client.get("/api/notifications/subscriptions/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 5)
        self.assertEqual(res.data[4]["id"], str(self.person_subscription.id))


class CreateSubscriptionsAPITestCase(APITestCase):
    def setUp(self):
        signals.post_save.disconnect(
            sender=Membership, dispatch_uid="create_default_membership_subscriptions"
        )
        self.person = Person.objects.create_person(
            email="person@example.com", create_role=True
        )
        self.other_person = Person.objects.create_person(
            email="other_person@example.com", create_role=True
        )

        self.person_group = SupportGroup.objects.create()
        self.other_person_group = SupportGroup.objects.create()

        self.person_membership = Membership.objects.create(
            supportgroup=self.person_group,
            person=self.person,
            membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )
        self.other_person_membership = Membership.objects.create(
            supportgroup=self.other_person_group,
            person=self.other_person,
            membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )

        self.person_subscription = Subscription.objects.create(
            person=self.person,
            type=Subscription.SUBSCRIPTION_PUSH,
            activity_type=Activity.TYPE_WAITING_LOCATION_GROUP,
            membership=self.person_membership,
        )
        self.other_person_subscription = Subscription.objects.create(
            person=self.other_person,
            type=Subscription.SUBSCRIPTION_PUSH,
            activity_type=Activity.TYPE_EVENT_UPDATE,
        )

        self.valid_data = {
            "type": Subscription.SUBSCRIPTION_PUSH,
            "activityType": Activity.TYPE_GROUP_INVITATION,
            "group": None,
        }

    def test_anonymous_person_cannot_create_subscriptions(self):
        self.client.logout()
        res = self.client.post(
            "/api/notifications/subscriptions/", data=[self.valid_data]
        )
        self.assertEqual(res.status_code, 401)

    def test_authenticated_person_cannot_create_subscriptions_without_type(self):
        self.client.force_login(self.person.role)
        res = self.client.post(
            "/api/notifications/subscriptions/",
            data=[{**self.valid_data, "type": None}],
        )
        self.assertEqual(res.status_code, 422)
        self.assertIn("type", res.data[0])

    def test_authenticated_person_cannot_create_subscriptions_with_invalid_type(self):
        self.client.force_login(self.person.role)
        res = self.client.post(
            "/api/notifications/subscriptions/",
            data=[{**self.valid_data, "type": "unexisting-type"}],
        )
        self.assertEqual(res.status_code, 422)
        self.assertIn("type", res.data[0])

    def test_authenticated_person_cannot_create_subscriptions_without_activity_type(
        self,
    ):
        self.client.force_login(self.person.role)
        res = self.client.post(
            "/api/notifications/subscriptions/",
            data=[{**self.valid_data, "activityType": None}],
        )
        self.assertEqual(res.status_code, 422)
        self.assertIn("activityType", res.data[0])

    def test_authenticated_person_cannot_create_subscriptions_with_invalid_activity_type(
        self,
    ):
        self.client.force_login(self.person.role)
        res = self.client.post(
            "/api/notifications/subscriptions/",
            data=[{**self.valid_data, "activityType": "unexisting-activity-type"}],
        )
        self.assertEqual(res.status_code, 422)
        self.assertIn("activityType", res.data[0])

    def test_authenticated_person_cannot_create_subscriptions_with_unexisting_group(
        self,
    ):
        self.client.force_login(self.person.role)
        res = self.client.post(
            "/api/notifications/subscriptions/",
            data=[{**self.valid_data, "group": str(uuid.uuid4())}],
        )
        self.assertEqual(res.status_code, 422)
        self.assertIn("group", res.data[0])

    def test_authenticated_person_cannot_create_subscriptions_with_a_group_without_membership(
        self,
    ):
        self.client.force_login(self.person.role)
        res = self.client.post(
            "/api/notifications/subscriptions/",
            data=[{**self.valid_data, "group": str(self.other_person_group.pk)}],
        )
        self.assertEqual(res.status_code, 422)
        self.assertIn("group", res.data[0])

    def test_authenticated_person_cannot_create_subscriptions_that_already_exist(
        self,
    ):
        self.client.force_login(self.person.role)
        existing_subscription_data = {
            "type": self.person_subscription.type,
            "activityType": self.person_subscription.activity_type,
            "group": str(self.person_subscription.membership.supportgroup.pk),
        }
        res = self.client.post(
            "/api/notifications/subscriptions/",
            data=[existing_subscription_data],
        )
        self.assertEqual(res.status_code, 422)
        self.assertIn("global", res.data)

    def test_authenticated_person_can_create_subscriptions_with_valid_data(
        self,
    ):
        self.client.force_login(self.person.role)
        subscription_without_group = {**self.valid_data, "group": None}
        subscription_with_group = {
            **self.valid_data,
            "group": str(self.person_group.pk),
        }
        res = self.client.post(
            "/api/notifications/subscriptions/",
            data=[subscription_without_group, subscription_with_group],
        )
        self.assertEqual(res.status_code, 201)
        self.assertEqual(len(res.data), 2)


class DeleteSubscriptionsAPITestCase(APITestCase):
    def setUp(self):
        signals.post_save.disconnect(
            sender=Membership, dispatch_uid="create_default_membership_subscriptions"
        )
        self.person = Person.objects.create_person(
            email="person@example.com", create_role=True
        )
        self.other_person = Person.objects.create_person(
            email="other_person@example.com", create_role=True
        )

        self.person_subscription = Subscription.objects.create(
            person=self.person,
            type=Subscription.SUBSCRIPTION_PUSH,
            activity_type=Activity.TYPE_WAITING_LOCATION_GROUP,
        )
        self.other_person_subscription = Subscription.objects.create(
            person=self.other_person,
            type=Subscription.SUBSCRIPTION_PUSH,
            activity_type=Activity.TYPE_EVENT_UPDATE,
        )

        self.valid_data = [str(self.person_subscription.pk)]

    def test_anonymous_person_cannot_delete_subscriptions(self):
        self.client.logout()
        res = self.client.delete(
            "/api/notifications/subscriptions/", data=self.valid_data
        )
        self.assertEqual(res.status_code, 401)

    def test_authenticated_person_cannot_delete_another_person_subscriptions(self):
        self.client.force_login(self.person.role)
        res = self.client.delete(
            "/api/notifications/subscriptions/",
            data=[str(self.other_person_subscription.pk)],
        )
        self.assertEqual(res.status_code, 204)
        self.assertTrue(
            Subscription.objects.filter(pk=self.other_person_subscription.pk).exists()
        )

    def test_authenticated_person_can_delete_own_subscriptions(self):
        self.client.force_login(self.person.role)
        res = self.client.delete(
            "/api/notifications/subscriptions/",
            data=[str(self.person_subscription.pk)],
        )
        self.assertEqual(res.status_code, 204)
        self.assertFalse(
            Subscription.objects.filter(pk=self.person_subscription.pk).exists()
        )
