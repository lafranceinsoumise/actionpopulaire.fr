from django.utils import timezone
from rest_framework.test import APITestCase

from agir.events.models import Event
from agir.groups.models import SupportGroup, Membership
from agir.msgs.models import SupportGroupMessage, SupportGroupMessageComment
from agir.people.models import Person


class GroupMessagesTestAPICase(APITestCase):
    def setUp(self):
        self.group = SupportGroup.objects.create()
        self.manager = Person.objects.create_person(
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
        self.member = Person.objects.create_person(
            email="member@example.com",
            create_role=True,
        )
        Membership.objects.create(
            supportgroup=self.group,
            person=self.member,
            membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
        )
        self.non_member = Person.objects.create_person(
            email="non_member@example.com", create_role=True
        )
        now = timezone.now()
        day = timezone.timedelta(days=1)
        hour = timezone.timedelta(hours=1)
        self.event = Event.objects.create(
            name="événement test pour groupe",
            start_time=now + 3 * day,
            end_time=now + 3 * day + 4 * hour,
        )

    def test_member_can_get_messages(self):
        message = SupportGroupMessage.objects.create(
            supportgroup=self.group, author=self.manager, text="Lorem"
        )
        self.client.force_login(self.member.role)
        res = self.client.get(f"/api/groupes/{self.group.pk}/messages/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["results"][0]["id"], str(message.id))
        self.assertEqual(
            res.data["results"][0]["author"],
            {
                "id": str(self.manager.id),
                "displayName": self.manager.display_name,
                "image": None,
            },
        )
        self.assertEqual(res.data["results"][0]["text"], "Lorem")
        # self.assertEqual(res.data["results"][0]["image"], None)
        self.assertIn("recentComments", res.data["results"][0])
        self.assertIn("commentCount", res.data["results"][0])
        self.assertNotIn("comments", res.data["results"][0])

    def test_deleted_messages_are_hidden(self):
        SupportGroupMessage.objects.create(
            supportgroup=self.group, author=self.manager, text="Lorem", deleted=True
        )
        self.client.force_login(self.member.role)
        res = self.client.get(f"/api/groupes/{self.group.pk}/messages/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["results"], [])

    def test_message_from_inactive_people_are_hidden(self):
        message = SupportGroupMessage.objects.create(
            supportgroup=self.group, author=self.manager, text="Lorem"
        )

        self.member2 = Person.objects.create_person(
            email="member2@example.com",
            create_role=True,
        )
        Membership.objects.create(
            supportgroup=self.group,
            person=self.member2,
            membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
        )
        SupportGroupMessageComment.objects.create(
            author=self.member2, message=message, text="Comment"
        )
        self.member2.role.is_active = False
        self.member2.role.save()

        self.client.force_login(self.member.role)
        res = self.client.get(f"/api/groupes/{self.group.pk}/messages/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data["results"]), 1)

    def create_other_manager(self):
        self.other_manager = Person.objects.create_person(
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

    def test_not_login_cannot_get_messages(self):
        SupportGroupMessage.objects.create(
            supportgroup=self.group, author=self.manager, text="Lorem"
        )
        res = self.client.get(f"/api/groupes/{self.group.pk}/messages/")
        self.assertEqual(res.status_code, 401)

    def test_manager_can_post_message_without_event(self):
        self.client.force_login(self.manager.role)
        res = self.client.post(
            f"/api/groupes/{self.group.pk}/messages/", data={"text": "Lorem"}
        )
        self.assertEqual(res.status_code, 201)
        self.assertEqual(self.group.messages.first().text, "Lorem")
        self.assertEqual(self.group.messages.first().linked_event, None)

    def test_manager_can_post_message_with_null_event(self):
        self.client.force_login(self.manager.role)
        res = self.client.post(
            f"/api/groupes/{self.group.pk}/messages/",
            data={"text": "Lorem", "linkedEvent": None},
        )
        self.assertEqual(res.status_code, 201)
        self.assertEqual(self.group.messages.first().text, "Lorem")
        self.assertEqual(self.group.messages.first().linked_event, None)

    def test_manager_can_post_message_with_event(self):
        self.client.force_login(self.manager.role)
        res = self.client.post(
            f"/api/groupes/{self.group.pk}/messages/",
            data={"text": "Lorem", "linkedEvent": str(self.event.pk)},
        )
        self.assertEqual(res.status_code, 201)
        self.assertEqual(self.group.messages.first().text, "Lorem")
        self.assertEqual(self.group.messages.first().linked_event, self.event)

    def test_member_cannot_post_message(self):
        self.client.force_login(self.member.role)
        res = self.client.post(
            f"/api/groupes/{self.group.pk}/messages/", data={"text": "Lorem"}
        )
        self.assertEqual(res.status_code, 403)

    def test_member_can_get_single_message(self):
        message = SupportGroupMessage.objects.create(
            supportgroup=self.group, author=self.manager, text="Lorem"
        )
        self.client.force_login(self.member.role)
        res = self.client.get(
            f"/api/groupes/messages/{message.pk}/",
            data={"text": "Ipsum"},
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["id"], str(message.id))
        self.assertEqual(
            res.data["author"],
            {
                "id": str(self.manager.id),
                "displayName": self.manager.display_name,
                "image": None,
            },
        )
        self.assertEqual(res.data["text"], "Lorem")
        # self.assertEqual(res.data["image"], None)
        self.assertEqual(
            res.data["group"],
            {"id": self.group.id, "name": self.group.name, "isManager": False},
        )
        self.assertNotIn("recentComments", res.data)

    def test_member_cannot_get_single_deleted_message(self):
        message = SupportGroupMessage.objects.create(
            supportgroup=self.group, author=self.manager, text="Lorem", deleted=True
        )
        self.client.force_login(self.member.role)
        res = self.client.get(
            f"/api/groupes/messages/{message.pk}/",
            data={"text": "Ipsum"},
        )
        self.assertEqual(res.status_code, 404)

    def test_non_member_cannot_get_single_message(self):
        message = SupportGroupMessage.objects.create(
            supportgroup=self.group, author=self.manager, text="Lorem"
        )
        self.client.force_login(self.non_member.role)
        res = self.client.get(f"/api/groupes/messages/{message.pk}/")
        self.assertEqual(res.status_code, 403)

    def test_author_can_edit_message(self):
        message = SupportGroupMessage.objects.create(
            supportgroup=self.group, author=self.manager, text="Lorem"
        )
        self.client.force_login(self.manager.role)
        res = self.client.patch(
            f"/api/groupes/messages/{message.pk}/",
            data={"text": "Ipsum"},
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
            f"/api/groupes/messages/{message.pk}/",
            data={"text": "Ipsum"},
        )
        self.assertEqual(res.status_code, 403)

    def test_author_can_delete_own_message(self):
        message = SupportGroupMessage.objects.create(
            supportgroup=self.group, author=self.manager, text="Lorem"
        )
        self.client.force_login(self.manager.role)
        res = self.client.delete(f"/api/groupes/messages/{message.pk}/")
        self.assertEqual(res.status_code, 204)
        self.assertEqual(self.group.messages.first().deleted, True)

    def test_other_group_managers_can_delete_group_messages(self):
        message = SupportGroupMessage.objects.create(
            supportgroup=self.group, author=self.manager, text="Lorem"
        )
        self.create_other_manager()
        self.client.force_login(self.other_manager.role)
        res = self.client.delete(f"/api/groupes/messages/{message.pk}/")
        self.assertEqual(res.status_code, 204)

    def test_cannot_retrieve_private_messages_if_group_messaging_is_disabled(self):
        group = SupportGroup.objects.create(
            name="No messages !", is_private_messaging_enabled=False
        )
        Membership.objects.create(
            person=self.manager,
            supportgroup=group,
            membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )
        message = SupportGroupMessage.objects.create(
            supportgroup=group,
            author=self.manager,
            text="Lorem",
            required_membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )
        self.client.force_login(self.manager.role)
        res = self.client.get(f"/api/groupes/{group.pk}/messages/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["count"], 0)
        res = self.client.get(f"/api/groupes/messages/{message.pk}/")
        self.assertEqual(res.status_code, 404)

    def test_cannot_lock_message_if_not_allowed(self):
        group = SupportGroup.objects.create(name="No messages !")
        message = SupportGroupMessage.objects.create(
            supportgroup=group, author=self.manager, text="Lorem"
        )

        self.client.force_login(self.member.role)
        res = self.client.patch(
            f"/api/groupes/messages/{message.pk}/",
            data={"isLocked": True},
        )
        self.assertEqual(res.status_code, 403)

    def test_manager_can_lock_message(self):
        group = SupportGroup.objects.create(name="No messages !")
        Membership.objects.create(
            person=self.manager,
            supportgroup=group,
            membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )
        message = SupportGroupMessage.objects.create(
            supportgroup=group, author=self.manager, text="Lorem"
        )

        self.client.force_login(self.manager.role)
        res = self.client.patch(
            f"/api/groupes/messages/{message.pk}/",
            data={"isLocked": True},
        )
        self.assertEqual(res.status_code, 200)
        pass


class GroupMessageCommentAPITestCase(APITestCase):
    def setUp(self):
        self.group = SupportGroup.objects.create()
        self.manager = Person.objects.create_person(
            first_name="Jean-Luc",
            last_name="Mélenchon",
            display_name="JLM",
            email="manager@example.com",
            create_role=True,
        )
        Membership.objects.create(
            supportgroup=self.group,
            person=self.manager,
            membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )
        self.member = Person.objects.create_person(
            first_name="Jill Maud",
            last_name="Royer",
            display_name="Jill",
            email="member@example.com",
            create_role=True,
        )
        Membership.objects.create(
            supportgroup=self.group,
            person=self.member,
            membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
        )
        self.non_member = Person.objects.create_person(
            email="non_member@example.com", create_role=True
        )
        self.message = SupportGroupMessage.objects.create(
            supportgroup=self.group, author=self.manager, text="Lorem"
        )

    def create_other_member(self):
        self.other_member = Person.objects.create_person(
            email="other_member@example.com",
            create_role=True,
        )
        Membership.objects.create(
            supportgroup=self.group,
            person=self.other_member,
            membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
        )

    def test_member_can_get_message_comments(self):
        comment = SupportGroupMessageComment.objects.create(
            message=self.message, author=self.member, text="Lorem"
        )
        self.client.force_login(self.member.role)
        res = self.client.get(f"/api/groupes/messages/{self.message.pk}/comments/")
        self.assertEqual(res.status_code, 200)
        results = res.data["results"]
        self.assertEqual(results[0]["id"], str(comment.pk))
        self.assertEqual(
            results[0]["author"],
            {
                "id": str(self.member.id),
                "displayName": self.member.display_name,
                "image": None,
            },
        )
        self.assertEqual(results[0]["text"], "Lorem")
        self.assertEqual(results[0]["image"], None)

    def test_deleted_comments_are_hidden(self):
        SupportGroupMessageComment.objects.create(
            message=self.message, author=self.member, text="Lorem", deleted=True
        )
        self.client.force_login(self.member.role)
        res = self.client.get(f"/api/groupes/messages/{self.message.pk}/comments/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["results"], [])

    def test_non_member_cannot_get_message_comments(self):
        SupportGroupMessageComment.objects.create(
            message=self.message, author=self.member, text="Lorem"
        )
        self.client.force_login(self.non_member.role)
        res = self.client.get(f"/api/groupes/messages/{self.message.pk}/comments/")
        self.assertEqual(res.status_code, 403)

    def test_member_can_post_comment(self):
        self.client.force_login(self.member.role)
        res = self.client.post(
            f"/api/groupes/messages/{self.message.pk}/comments/",
            data={"text": "Lorem"},
        )
        self.assertEqual(res.status_code, 201)
        self.assertEqual(self.message.comments.first().text, "Lorem")

    def test_non_member_cannot_post_comment(self):
        self.client.force_login(self.non_member.role)
        res = self.client.post(
            f"/api/groupes/messages/{self.message.pk}/comments/",
            data={"text": "Lorem"},
        )
        self.assertEqual(res.status_code, 403)

    def test_author_can_edit_comment(self):
        comment = SupportGroupMessageComment.objects.create(
            message=self.message, author=self.member, text="Lorem"
        )
        self.client.force_login(self.member.role)
        res = self.client.patch(
            f"/api/groupes/messages/comments/{comment.pk}/",
            data={"text": "Ipsum"},
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(self.message.comments.first().text, "Ipsum")

    def test_non_author_cannot_edit_comment(self):
        comment = SupportGroupMessageComment.objects.create(
            message=self.message, author=self.member, text="Lorem"
        )
        self.create_other_member()
        self.client.force_login(self.other_member.role)
        res = self.client.patch(
            f"/api/groupes/messages/comments/{comment.pk}/",
            data={"text": "Ipsum"},
        )
        self.assertEqual(res.status_code, 403)

    def test_author_can_delete_comment(self):
        comment = SupportGroupMessageComment.objects.create(
            message=self.message, author=self.member, text="Lorem"
        )
        self.client.force_login(self.member.role)
        res = self.client.delete(f"/api/groupes/messages/comments/{comment.pk}/")
        self.assertEqual(res.status_code, 204)
        self.assertEqual(self.message.comments.first().deleted, True)

    def test_non_author_cannot_delete_comment(self):
        comment = SupportGroupMessageComment.objects.create(
            message=self.message, author=self.member, text="Lorem"
        )
        self.create_other_member()
        self.client.force_login(self.other_member.role)
        res = self.client.delete(f"/api/groupes/messages/comments/{comment.pk}/")
        self.assertEqual(res.status_code, 403)

    def test_manager_can_delete_comment(self):
        comment = SupportGroupMessageComment.objects.create(
            message=self.message, author=self.member, text="Lorem"
        )
        self.client.force_login(self.manager.role)
        res = self.client.delete(f"/api/groupes/messages/comments/{comment.pk}/")
        self.assertEqual(res.status_code, 204)
        self.assertEqual(self.message.comments.first().deleted, True)

    def test_cannot_retrieve_private_message_comments_if_group_messaging_is_disabled(
        self,
    ):
        group = SupportGroup.objects.create(
            name="No messages !", is_private_messaging_enabled=False
        )
        Membership.objects.create(
            person=self.manager,
            supportgroup=group,
            membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )
        message = SupportGroupMessage.objects.create(
            supportgroup=group,
            author=self.manager,
            text="Lorem",
            required_membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )
        SupportGroupMessageComment.objects.create(
            message=message, author=self.manager, text="Lorem"
        )
        self.client.force_login(self.manager.role)
        res = self.client.get(f"/api/groupes/messages/{message.pk}/comments/")
        self.assertEqual(res.status_code, 404)

    def test_cannot_send_comments_if_message_locked(self):
        self.message.is_locked = True
        self.message.save()
        self.client.force_login(self.member.role)
        res = self.client.post(
            f"/api/groupes/messages/{self.message.pk}/comments/",
            data={"text": "Lorem"},
        )
        self.assertEqual(res.status_code, 403)

    def test_cannot_send_comments_if_message_is_readonly(self):
        self.message.readonly = True
        self.message.save()
        self.client.force_login(self.member.role)
        res = self.client.post(
            f"/api/groupes/messages/{self.message.pk}/comments/",
            data={"text": "Lorem"},
        )
        self.assertEqual(res.status_code, 403)
