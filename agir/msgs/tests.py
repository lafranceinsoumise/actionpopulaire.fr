from rest_framework.test import APITestCase

from agir.groups.models import SupportGroup, Membership
from agir.msgs.actions import (
    update_recipient_message,
    get_unread_message_count,
    get_message_unread_comment_count,
)
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
            email="member@example.com",
            create_role=True,
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
        self.user = Person.objects.create(
            email="user@example.com",
            create_role=True,
        )
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
        self.user = Person.objects.create(
            email="user@example.com",
            create_role=True,
        )
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


class UpdateRecipientMessageActionTestCase(APITestCase):
    def test_recipient_message_modified_field_is_updated(self):
        supportgroup = SupportGroup.objects.create()
        recipient = Person.objects.create(email="recipient@agis.msgs", create_role=True)
        message = SupportGroupMessage.objects.create(
            author=recipient, supportgroup=supportgroup
        )
        qs = SupportGroupMessageRecipient.objects.filter(
            recipient=recipient, message=message
        )
        self.assertEqual(qs.count(), 0)
        update_recipient_message(message, recipient)
        self.assertEqual(qs.count(), 1)
        original_modified = qs.first().modified
        update_recipient_message(message, recipient)
        self.assertEqual(qs.count(), 1)
        self.assertTrue(qs.first().modified > original_modified)


class UserUnreadMessageCountAPITestCase(APITestCase):
    def setUp(self):
        self.group = SupportGroup.objects.create()
        self.user = Person.objects.create(
            email="user@example.com",
            create_role=True,
        )
        Membership.objects.create(
            person=self.user,
            supportgroup=self.group,
            membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )

    def test_unauthenticated_user_cannot_get_message_recipients(self):
        self.client.logout()
        response = self.client.get("/api/user/messages/unread_count/")
        self.assertEqual(response.status_code, 401)

    def test_authenticated_user_can_get_message_recipients(self):
        self.client.force_login(self.user.role)
        response = self.client.get("/api/user/messages/unread_count/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("unreadMessageCount", response.data)


class GetUnreadMessageCountActionTestCase(APITestCase):
    def setUp(self):
        self.supportgroup = SupportGroup.objects.create()
        self.reader = Person.objects.create(email="reader@agis.msgs", create_role=True)
        self.writer = Person.objects.create(email="writer@agir.msgs", create_role=True)
        Membership.objects.create(supportgroup=self.supportgroup, person=self.reader)
        Membership.objects.create(supportgroup=self.supportgroup, person=self.writer)

    def test_group_messages_before_membership_creation_are_not_counted(self):
        supportgroup = SupportGroup.objects.create()
        writer = Person.objects.create(email="writer@group.com", create_role=True)
        new_member = Person.objects.create(
            email="new_member@group.com", create_role=True
        )

        # A message is created before the person joins the group
        message = SupportGroupMessage.objects.create(
            author=writer, supportgroup=supportgroup, text="1"
        )

        # A comment for the message is created before the person joins the group
        SupportGroupMessageComment.objects.create(
            author=writer, message=message, text="1.1"
        )
        unread_message_count = get_unread_message_count(new_member.pk)
        self.assertEqual(unread_message_count, 0)

        # The person joins the group
        Membership.objects.create(supportgroup=supportgroup, person=new_member)
        unread_message_count = get_unread_message_count(new_member.pk)
        self.assertEqual(unread_message_count, 0)

        # A second comment for the message is created after the person has joined the group
        SupportGroupMessageComment.objects.create(
            author=writer, message=message, text="1.2"
        )
        unread_message_count = get_unread_message_count(new_member.pk)
        self.assertEqual(unread_message_count, 1)

        # A second message is created after the person has joined the group
        SupportGroupMessage.objects.create(
            author=writer, supportgroup=supportgroup, text="2"
        )
        unread_message_count = get_unread_message_count(new_member.pk)
        self.assertEqual(unread_message_count, 2)

    def test_get_unread_message_count(self):
        # No messages
        unread_message_count = get_unread_message_count(self.reader.pk)
        self.assertEqual(unread_message_count, 0)

        # One unread message
        message = SupportGroupMessage.objects.create(
            author=self.writer, supportgroup=self.supportgroup, text="1"
        )
        unread_message_count = get_unread_message_count(self.reader.pk)
        self.assertEqual(unread_message_count, 1)

        # One unread message with one unread comment
        SupportGroupMessageComment.objects.create(
            author=self.writer, message=message, text="1.1"
        )
        unread_message_count = get_unread_message_count(self.reader.pk)
        self.assertEqual(unread_message_count, 2)

        # One unread message with two unread comments (one written by the recipient)
        SupportGroupMessageComment.objects.create(
            author=self.reader, message=message, text="1.2"
        )
        unread_message_count = get_unread_message_count(self.reader.pk)
        self.assertEqual(unread_message_count, 2)

        # One unread message with two unread comments
        # (one written by the recipient and one deleted)
        SupportGroupMessageComment.objects.update(
            author=self.writer, message=message, text="1.1", deleted=True
        )
        unread_message_count = get_unread_message_count(self.reader.pk)
        self.assertEqual(unread_message_count, 1)

        # One read message with no unread comments
        SupportGroupMessageRecipient.objects.create(
            recipient=self.reader, message=message
        )
        unread_message_count = get_unread_message_count(self.reader.pk)
        self.assertEqual(unread_message_count, 0)

        # One read message with one unread comment
        SupportGroupMessageComment.objects.create(
            author=self.writer, message=message, text="1.3"
        )
        unread_message_count = get_unread_message_count(self.reader.pk)
        self.assertEqual(unread_message_count, 1)

        # One read message with one unread comment and one unread message with no comments
        SupportGroupMessage.objects.create(
            author=self.writer, supportgroup=self.supportgroup, text="2"
        )
        unread_message_count = get_unread_message_count(self.reader.pk)
        self.assertEqual(unread_message_count, 2)

        # One read message with one unread comment,
        # one unread message with no comments,
        # and one unread deleted message
        SupportGroupMessage.objects.create(
            author=self.writer, supportgroup=self.supportgroup, text="3", deleted=True
        )
        unread_message_count = get_unread_message_count(self.reader.pk)
        self.assertEqual(unread_message_count, 2)

        # One read message with one unread comment,
        # one unread message with no comments,
        # one unread deleted message,
        # one unread message written by the recipient
        SupportGroupMessage.objects.create(
            author=self.reader, supportgroup=self.supportgroup, text="3", deleted=True
        )
        unread_message_count = get_unread_message_count(self.reader.pk)
        self.assertEqual(unread_message_count, 2)


class GetUnreadMessageCommentCountActionTestCase(APITestCase):
    def setUp(self):
        self.supportgroup = SupportGroup.objects.create()
        self.reader = Person.objects.create(email="reader@agis.msgs", create_role=True)
        self.writer = Person.objects.create(email="writer@agir.msgs", create_role=True)
        Membership.objects.create(supportgroup=self.supportgroup, person=self.writer)
        self.message = SupportGroupMessage.objects.create(
            author=self.writer, supportgroup=self.supportgroup, text="1"
        )

    def test_comments_before_membership_creation_are_not_counted(self):
        # A comment for the message is created before the person joins the group
        SupportGroupMessageComment.objects.create(
            author=self.writer, message=self.message, text="1.1"
        )
        unread_comment_count = get_message_unread_comment_count(
            self.reader.pk, self.message.pk
        )
        self.assertEqual(unread_comment_count, 0)

        # The person joins the group
        Membership.objects.create(supportgroup=self.supportgroup, person=self.reader)
        unread_comment_count = get_message_unread_comment_count(
            self.reader.pk, self.message.pk
        )
        self.assertEqual(unread_comment_count, 0)

        # A second comment for the message is created after the person has joined the group
        SupportGroupMessageComment.objects.create(
            author=self.writer, message=self.message, text="1.2"
        )
        unread_comment_count = get_message_unread_comment_count(
            self.reader.pk, self.message.pk
        )
        self.assertEqual(unread_comment_count, 1)

        # The message and its comment are read
        SupportGroupMessageRecipient.objects.create(
            recipient=self.reader, message=self.message
        )
        unread_comment_count = get_message_unread_comment_count(
            self.reader.pk, self.message.pk
        )
        self.assertEqual(unread_comment_count, 0)

        # A third and fourth comment for the message is created
        SupportGroupMessageComment.objects.create(
            author=self.writer, message=self.message, text="1.3"
        )
        SupportGroupMessageComment.objects.create(
            author=self.writer, message=self.message, text="1.4"
        )
        unread_comment_count = get_message_unread_comment_count(
            self.reader.pk, self.message.pk
        )
        self.assertEqual(unread_comment_count, 2)
