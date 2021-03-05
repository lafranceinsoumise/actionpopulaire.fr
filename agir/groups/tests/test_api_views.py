from django.utils import timezone
from rest_framework.test import APITestCase
from unittest.mock import patch

from agir.groups.models import SupportGroup, Membership
from agir.people.models import Person


class GroupJoinAPITestCase(APITestCase):
    def setUp(self):
        self.person = Person.objects.create(
            email="person@example.com",
            create_role=True,
            is_insoumise=True,
            is_2022=True,
        )

    def test_anonymous_person_cannot_join(self):
        self.client.logout()
        group = SupportGroup.objects.create()
        res = self.client.post(f"/api/groupes/{group.pk}/rejoindre/")
        self.assertEqual(res.status_code, 403)
        self.assertIn("redirectTo", res.data)

    def test_2022_person_cannot_join_insoumise_group(self):
        person_2022 = Person.objects.create(
            email="2022@example.com",
            create_role=True,
            is_insoumise=False,
            is_2022=True,
        )
        group_insoumise = SupportGroup.objects.create(
            type=SupportGroup.TYPE_LOCAL_GROUP
        )
        self.client.force_login(person_2022.role)
        res = self.client.post(f"/api/groupes/{group_insoumise.pk}/rejoindre/")
        self.assertEqual(res.status_code, 403)
        self.assertIn("redirectTo", res.data)

    def test_insoumise_person_cannot_join_2022_group(self):
        person_insoumise = Person.objects.create(
            email="insoumise@example.com",
            create_role=True,
            is_insoumise=True,
            is_2022=False,
        )
        group_2022 = SupportGroup.objects.create(type=SupportGroup.TYPE_2022)
        self.client.force_login(person_insoumise.role)
        res = self.client.post(f"/api/groupes/{group_2022.pk}/rejoindre/")
        self.assertEqual(res.status_code, 403)
        self.assertIn("redirectTo", res.data)

    def test_person_cannot_join_full_2022_group(self):
        self.client.force_login(self.person.role)
        full_group = SupportGroup.objects.create(type=SupportGroup.TYPE_2022)
        for i in range(SupportGroup.MEMBERSHIP_LIMIT + 1):
            member = Person.objects.create(email=f"member_{i}@example.com")
            Membership.objects.create(
                supportgroup=full_group,
                person=member,
                membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
            )
        res = self.client.post(f"/api/groupes/{full_group.pk}/rejoindre/")
        self.assertEqual(res.status_code, 403)
        self.assertIn("redirectTo", res.data)

    def test_person_cannot_join_if_already_member(self):
        person_group = SupportGroup.objects.create()
        Membership.objects.create(
            supportgroup=person_group,
            person=self.person,
            membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
        )
        self.client.force_login(self.person.role)
        res = self.client.post(f"/api/groupes/{person_group.pk}/rejoindre/")
        self.assertEqual(res.status_code, 403)
        self.assertIn("redirectTo", res.data)

    def test_authenticated_person_can_join_available_group(self):
        group = SupportGroup.objects.create()
        self.client.force_login(self.person.role)
        res = self.client.post(f"/api/groupes/{group.pk}/rejoindre/")
        self.assertEqual(res.status_code, 201)

    def test_membership_is_created_upoin_joining(self):
        group = SupportGroup.objects.create()
        self.client.force_login(self.person.role)
        self.assertFalse(
            Membership.objects.filter(person=self.person, supportgroup=group).exists()
        )
        res = self.client.post(f"/api/groupes/{group.pk}/rejoindre/")
        self.assertEqual(res.status_code, 201)
        self.assertTrue(
            Membership.objects.filter(person=self.person, supportgroup=group).exists()
        )

    @patch("agir.groups.views.api_views.someone_joined_notification")
    def test_someone_joined_notification_is_sent_upon_joining(
        self, someone_joined_notification
    ):
        group = SupportGroup.objects.create()
        self.client.force_login(self.person.role)
        someone_joined_notification.assert_not_called()
        res = self.client.post(f"/api/groupes/{group.pk}/rejoindre/")
        self.assertEqual(res.status_code, 201)
        someone_joined_notification.assert_called()
