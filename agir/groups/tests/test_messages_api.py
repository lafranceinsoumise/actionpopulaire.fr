from rest_framework.test import APITestCase

from agir.groups.models import SupportGroup, Membership
from agir.msgs.models import SupportGroupMessage
from agir.people.models import Person


class GroupMessagesAPIViewTestCase(APITestCase):
    def setUp(self):
        self.group = SupportGroup.objects.create()
        self.manager = Person.objects.create(
            first_name="Jean-Luc",
            last_name="Mélenchon",
            email="manager@example.com",
            create_role=True,
        )
        Membership.objects.create(
            supportgroup=self.group,
            person=self.manager,
            membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )
        self.member = Person.objects.create(
            email="member@example.com", create_role=True
        )
        Membership.objects.create(
            supportgroup=self.group, person=self.member,
        )
        self.non_member = Person.objects.create(
            email="non_member@example.com", create_role=True
        )

    def test_member_can_get_messages(self):
        message = SupportGroupMessage.objects.create(
            supportgroup=self.group, author=self.manager, text="Lorem"
        )
        self.client.force_login(self.member.role)
        res = self.client.get(f"/api/groupes/{self.group.pk}/messages/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            res.data,
            [
                {
                    "id": str(message.id),
                    "author": {"displayName": "Jean-Luc Mélenchon"},
                    "text": "Lorem",
                    "image": None,
                    "supportgroup": {
                        "id": str(self.group.id),
                        "name": self.group.name,
                    },
                }
            ],
        )

    def create_other_manager(self):
        self.other_manager = Person.objects.create(
            first_name="Mathilde",
            last_name="Panot",
            email="manager2@example.com",
            create_role=True,
        )
        Membership.objects.create(
            supportgroup=self.group,
            person=self.other_manager,
            membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )

    def test_not_member_cannot_get_messages(self):
        SupportGroupMessage.objects.create(
            supportgroup=self.group, author=self.manager, text="Lorem"
        )
        self.client.force_login(self.non_member.role)
        res = self.client.get(f"/api/groupes/{self.group.pk}/messages/")
        self.assertEqual(res.status_code, 403)

    def test_manager_can_post_message(self):
        self.client.force_login(self.manager.role)
        res = self.client.post(
            f"/api/groupes/{self.group.pk}/messages/", data={"text": "Lorem"}
        )
        self.assertEqual(res.status_code, 201)
        self.assertEqual(self.group.messages.first().text, "Lorem")

    def test_member_cannot_post_message(self):
        self.client.force_login(self.member.role)
        res = self.client.post(
            f"/api/groupes/{self.group.pk}/messages/", data={"text": "Lorem"}
        )
        self.assertEqual(res.status_code, 403)

    def test_author_can_edit_message(self):
        message = SupportGroupMessage.objects.create(
            supportgroup=self.group, author=self.manager, text="Lorem"
        )
        self.client.force_login(self.manager.role)
        res = self.client.patch(
            f"/api/groupes/messages/{message.pk}/", data={"text": "Ipsum"}
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(self.group.messages.first().text, "Ipsum")

    def test_non_author_cannot_edit_message(self):
        message = SupportGroupMessage.objects.create(
            supportgroup=self.group, author=self.manager, text="Lorem"
        )
        self.create_other_manager()
        self.client.force_login(self.other_manager.role)
        res = self.client.put(
            f"/api/groupes/messages/{message.pk}/", data={"text": "Ipsum"}
        )
        self.assertEqual(res.status_code, 403)

    def test_author_can_delete_own_message(self):
        message = SupportGroupMessage.objects.create(
            supportgroup=self.group, author=self.manager, text="Lorem"
        )
        self.client.force_login(self.manager.role)
        res = self.client.delete(f"/api/groupes/messages/{message.pk}/")
        self.assertEqual(res.status_code, 204)
        self.assertFalse(self.group.messages.all().exists())

    def test_author_cannot_delete_own_message(self):
        message = SupportGroupMessage.objects.create(
            supportgroup=self.group, author=self.manager, text="Lorem"
        )
        self.create_other_manager()
        self.client.force_login(self.other_manager.role)
        res = self.client.delete(f"/api/groupes/messages/{message.pk}/")
        self.assertEqual(res.status_code, 403)
