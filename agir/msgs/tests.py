from rest_framework.test import APITestCase

from agir.groups.models import SupportGroup, Membership
from agir.msgs.models import (
    UserReport,
    SupportGroupMessage,
    SupportGroupMessageRecipient,
    SupportGroupMessageComment,
)
from agir.people.models import Person


class GroupMessagesTestAPICase(APITestCase):
    def setUp(self):
        self.manager = Person.objects.create(
            email="member@example.com", create_role=True,
        )
        self.group = SupportGroup.objects.create()
        Membership.objects.create(
            person=self.manager,
            supportgroup=self.group,
            membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )
        self.message = SupportGroupMessage.objects.create(
            supportgroup=self.group, author=self.manager, text="Lorem"
        )
        self.reporter = Person.objects.create(
            email="reporter@example.com", create_role=True
        )
        self.client.force_login(self.reporter.role)

    def test_can_user_report_message(self):
        res = self.client.post(
            "/api/report/",
            data={
                "content_type": "msgs.supportgroupmessage",
                "object_id": str(self.message.pk),
            },
        )
        self.assertEqual(res.status_code, 201)
        self.assertEqual(UserReport.objects.first().reported_object, self.message)


class UserMessageRecipientsAPITestCase(APITestCase):
    def setUp(self):
        self.group = SupportGroup.objects.create()
        self.user = Person.objects.create(email="user@example.com", create_role=True,)
        Membership.objects.create(
            person=self.user,
            supportgroup=self.group,
            membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )

    def test_unauthenticated_user_cannot_get_message_recipients(self):
        self.client.logout()
        response = self.client.get("/api/user/messages/recipients/")
        self.assertEqual(response.status_code, 401)

    def test_authenticated_user_can_get_message_recipients(self):
        user_managed_group = self.group
        user_non_managed_group = SupportGroup.objects.create()
        Membership.objects.create(
            person=self.user,
            supportgroup=user_non_managed_group,
            membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
        )
        user_extraneous_group = SupportGroup.objects.create()
        self.client.force_login(self.user.role)
        response = self.client.get("/api/user/messages/recipients/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], str(user_managed_group.id))


class UserMessagesAPITestCase(APITestCase):
    def setUp(self):
        self.group = SupportGroup.objects.create()
        self.user = Person.objects.create(email="user@example.com", create_role=True,)
        self.first_message = SupportGroupMessage.objects.create(
            author=self.user, supportgroup=self.group, text="First message"
        )
        Membership.objects.create(
            person=self.user,
            supportgroup=self.group,
            membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )

    def test_unauthenticated_user_cannot_get_messages(self):
        self.client.logout()
        response = self.client.get("/api/user/messages/")
        self.assertEqual(response.status_code, 401)

    def test_authenticated_user_can_get_messages(self):
        self.client.force_login(self.user.role)
        response = self.client.get("/api/user/messages/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], str(self.first_message.id))

    def test_authenticated_user_can_get_only_messages_from_his_her_groups(self):
        other_group = SupportGroup.objects.create()
        other_user = Person.objects.create(
            email="other_user@example.com", create_role=True
        )
        other_group_message = SupportGroupMessage.objects.create(
            author=other_user, supportgroup=other_group, text="Other text"
        )
        self.client.force_login(self.user.role)
        response = self.client.get("/api/user/messages/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], str(self.first_message.id))

    def test_authenticated_user_cannot_get_deleted_messages(self):
        self.first_message.deleted = True
        self.first_message.save()
        self.client.force_login(self.user.role)
        response = self.client.get("/api/user/messages/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_authenticated_user_can_get_messages_reading_state(self):
        SupportGroupMessage.objects.all().delete()
        read_message = SupportGroupMessage.objects.create(
            author=self.user, supportgroup=self.group, text="Read"
        )
        SupportGroupMessageRecipient.objects.create(
            message=read_message, recipient=self.user
        )
        unread_message = SupportGroupMessage.objects.create(
            author=self.user, supportgroup=self.group, text="Unread"
        )
        self.client.force_login(self.user.role)
        response = self.client.get("/api/user/messages/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["id"], str(unread_message.id))
        self.assertTrue(response.data[0]["isUnread"])
        self.assertEqual(response.data[1]["id"], str(read_message.id))
        self.assertFalse(response.data[1]["isUnread"])

    def test_authenticated_user_can_get_messages_unread_comment_counts(self):
        SupportGroupMessage.objects.all().delete()
        commenter = Person.objects.create(
            email="commenter@example.com", create_role=True
        )
        read_message = SupportGroupMessage.objects.create(
            author=self.user, supportgroup=self.group, text="Read"
        )

        self.client.force_login(self.user.role)
        response = self.client.get("/api/user/messages/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], str(read_message.id))
        self.assertEqual(response.data[0]["unreadCommentCount"], 0)
        self.assertTrue(response.data[0]["isUnread"])

        SupportGroupMessageComment.objects.create(
            author=commenter, message=read_message, text="Comment"
        )
        response = self.client.get("/api/user/messages/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], str(read_message.id))
        self.assertEqual(response.data[0]["unreadCommentCount"], 1)
        self.assertTrue(response.data[0]["isUnread"])

        SupportGroupMessageRecipient.objects.create(
            message=read_message, recipient=self.user
        )
        response = self.client.get("/api/user/messages/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], str(read_message.id))
        self.assertEqual(response.data[0]["unreadCommentCount"], 0)
        self.assertFalse(response.data[0]["isUnread"])

        SupportGroupMessageComment.objects.create(
            author=commenter, message=read_message, text="Comment"
        )
        response = self.client.get("/api/user/messages/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], str(read_message.id))
        self.assertEqual(response.data[0]["unreadCommentCount"], 1)
        self.assertFalse(response.data[0]["isUnread"])
