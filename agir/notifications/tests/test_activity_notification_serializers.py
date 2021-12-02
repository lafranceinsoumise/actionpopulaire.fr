from django.utils import timezone

from rest_framework.test import APITestCase

from agir.activity.models import Activity
from agir.events.models import Event
from agir.groups.models import SupportGroup
from agir.msgs.models import SupportGroupMessage, SupportGroupMessageComment
from agir.people.models import Person

from agir.notifications.serializers import ACTIVITY_NOTIFICATION_SERIALIZERS


class ActivityNotificationSerializersTestCase(APITestCase):
    def setUp(self):
        individual = Person.objects.create_person(
            email="individual@agir.test", display_name="individual"
        )
        recipient = Person.objects.create_person(
            email="recipient@agir.test", display_name="recipient"
        )
        supportgroup = SupportGroup.objects.create(name="Group")
        event = Event.objects.create(
            name="Event", start_time=timezone.now(), end_time=timezone.now()
        )
        supportgroup_message = SupportGroupMessage.objects.create(
            supportgroup=supportgroup,
            linked_event=event,
            text="A message",
            author=individual,
        )
        supportgroup_message_comment = SupportGroupMessageComment.objects.create(
            message=supportgroup_message, text="A comment", author=individual
        )
        meta = {
            "message": str(supportgroup_message.pk),
            "comment": str(supportgroup_message_comment.pk),
            "membershipLimitNotificationStep": 0,
            "membershipCount": 10,
            "changed_data": ["location", "start_time"],
            "transferredMemberships": 3,
            "oldGroup": supportgroup.name,
            "title": "Form title",
            "description": "...",
            "slug": "form-slug",
        }
        self.activity = Activity.objects.create(
            type=Activity.TYPE_NEW_MESSAGE,
            recipient=recipient,
            individual=individual,
            supportgroup=supportgroup,
            event=event,
            meta=meta,
        )

    def test_group_invitation_activity_type(self):
        self.activity.type = Activity.TYPE_GROUP_INVITATION
        serializer = ACTIVITY_NOTIFICATION_SERIALIZERS[self.activity.type]
        result = serializer(instance=self.activity)
        self.assertEqual(result.data.get("tag"), self.activity.type)
        self.assertIn("title", result.data)
        self.assertIn("body", result.data)
        self.assertIn("url", result.data)
        self.assertIn("icon", result.data)

    def test_new_follower_activity_type(self):
        self.activity.type = Activity.TYPE_NEW_FOLLOWER
        serializer = ACTIVITY_NOTIFICATION_SERIALIZERS[self.activity.type]
        result = serializer(instance=self.activity)
        self.assertEqual(result.data.get("tag"), self.activity.type)
        self.assertIn("title", result.data)
        self.assertIn("body", result.data)
        self.assertIn("url", result.data)
        self.assertIn("icon", result.data)

    def test_new_member_activity_type(self):
        self.activity.type = Activity.TYPE_NEW_MEMBER
        serializer = ACTIVITY_NOTIFICATION_SERIALIZERS[self.activity.type]
        result = serializer(instance=self.activity)
        self.assertEqual(result.data.get("tag"), self.activity.type)
        self.assertIn("title", result.data)
        self.assertIn("body", result.data)
        self.assertIn("url", result.data)
        self.assertIn("icon", result.data)

    def test_waiting_location_group_activity_type(self):
        self.activity.type = Activity.TYPE_WAITING_LOCATION_GROUP
        serializer = ACTIVITY_NOTIFICATION_SERIALIZERS[self.activity.type]
        result = serializer(instance=self.activity)
        self.assertEqual(result.data.get("tag"), self.activity.type)
        self.assertIn("title", result.data)
        self.assertIn("body", result.data)
        self.assertIn("url", result.data)
        self.assertIn("icon", result.data)

    def test_waiting_location_event_activity_type(self):
        self.activity.type = Activity.TYPE_WAITING_LOCATION_EVENT
        serializer = ACTIVITY_NOTIFICATION_SERIALIZERS[self.activity.type]
        result = serializer(instance=self.activity)
        self.assertEqual(result.data.get("tag"), self.activity.type)
        self.assertIn("title", result.data)
        self.assertIn("body", result.data)
        self.assertIn("url", result.data)
        self.assertIn("icon", result.data)

    def test_group_membership_limit_reminder_activity_type(self):
        self.activity.type = Activity.TYPE_WAITING_LOCATION_EVENT
        serializer = ACTIVITY_NOTIFICATION_SERIALIZERS[self.activity.type]
        for i in range(4):
            self.activity.meta["membershipLimitNotificationStep"] = i
            result = serializer(instance=self.activity)
            self.assertEqual(result.data.get("tag"), self.activity.type)
            self.assertIn("title", result.data)
            self.assertIn("body", result.data)
            self.assertIn("url", result.data)
            self.assertIn("icon", result.data)

    def test_group_info_update_activity_type(self):
        self.activity.type = Activity.TYPE_GROUP_INFO_UPDATE
        serializer = ACTIVITY_NOTIFICATION_SERIALIZERS[self.activity.type]
        result = serializer(instance=self.activity)
        self.assertEqual(result.data.get("tag"), self.activity.type)
        self.assertIn("title", result.data)
        self.assertIn("body", result.data)
        self.assertIn("url", result.data)
        self.assertIn("icon", result.data)

    def test_accepted_invitation_member_activity_type(self):
        self.activity.type = Activity.TYPE_ACCEPTED_INVITATION_MEMBER
        serializer = ACTIVITY_NOTIFICATION_SERIALIZERS[self.activity.type]
        result = serializer(instance=self.activity)
        self.assertEqual(result.data.get("tag"), self.activity.type)
        self.assertIn("title", result.data)
        self.assertIn("body", result.data)
        self.assertIn("url", result.data)
        self.assertIn("icon", result.data)

    def test_new_attendee_activity_type(self):
        self.activity.type = Activity.TYPE_NEW_ATTENDEE
        serializer = ACTIVITY_NOTIFICATION_SERIALIZERS[self.activity.type]
        result = serializer(instance=self.activity)
        self.assertEqual(result.data.get("tag"), self.activity.type)
        self.assertIn("title", result.data)
        self.assertIn("body", result.data)
        self.assertIn("url", result.data)
        self.assertIn("icon", result.data)

    def test_event_update_activity_type(self):
        self.activity.type = Activity.TYPE_EVENT_UPDATE
        serializer = ACTIVITY_NOTIFICATION_SERIALIZERS[self.activity.type]
        result = serializer(instance=self.activity)
        self.assertEqual(result.data.get("tag"), self.activity.type)
        self.assertIn("title", result.data)
        self.assertIn("body", result.data)
        self.assertIn("url", result.data)
        self.assertIn("icon", result.data)

    def test_new_event_mygroups_activity_type(self):
        self.activity.type = Activity.TYPE_NEW_EVENT_MYGROUPS
        serializer = ACTIVITY_NOTIFICATION_SERIALIZERS[self.activity.type]
        result = serializer(instance=self.activity)
        self.assertEqual(result.data.get("tag"), self.activity.type)
        self.assertIn("title", result.data)
        self.assertIn("body", result.data)
        self.assertIn("url", result.data)
        self.assertIn("icon", result.data)

    def test_new_report_activity_type(self):
        self.activity.type = Activity.TYPE_NEW_REPORT
        serializer = ACTIVITY_NOTIFICATION_SERIALIZERS[self.activity.type]
        result = serializer(instance=self.activity)
        self.assertEqual(result.data.get("tag"), self.activity.type)
        self.assertIn("title", result.data)
        self.assertIn("body", result.data)
        self.assertIn("url", result.data)
        self.assertIn("icon", result.data)

    def test_cancelled_event_activity_type(self):
        self.activity.type = Activity.TYPE_CANCELLED_EVENT
        serializer = ACTIVITY_NOTIFICATION_SERIALIZERS[self.activity.type]
        result = serializer(instance=self.activity)
        self.assertEqual(result.data.get("tag"), self.activity.type)
        self.assertIn("title", result.data)
        self.assertIn("body", result.data)
        self.assertIn("url", result.data)
        self.assertIn("icon", result.data)

    def test_group_coorganization_accepted_activity_type(self):
        self.activity.type = Activity.TYPE_GROUP_COORGANIZATION_ACCEPTED
        serializer = ACTIVITY_NOTIFICATION_SERIALIZERS[self.activity.type]
        result = serializer(instance=self.activity)
        self.assertEqual(result.data.get("tag"), self.activity.type)
        self.assertIn("title", result.data)
        self.assertIn("body", result.data)
        self.assertIn("url", result.data)
        self.assertIn("icon", result.data)

    def test_new_members_through_transfer_activity_type(self):
        self.activity.type = Activity.TYPE_NEW_MEMBERS_THROUGH_TRANSFER
        serializer = ACTIVITY_NOTIFICATION_SERIALIZERS[self.activity.type]
        result = serializer(instance=self.activity)
        self.assertEqual(result.data.get("tag"), self.activity.type)
        self.assertIn("title", result.data)
        self.assertIn("body", result.data)
        self.assertIn("url", result.data)
        self.assertIn("icon", result.data)

    def test_transferred_group_member_activity_type(self):
        self.activity.type = Activity.TYPE_TRANSFERRED_GROUP_MEMBER
        serializer = ACTIVITY_NOTIFICATION_SERIALIZERS[self.activity.type]
        result = serializer(instance=self.activity)
        self.assertEqual(result.data.get("tag"), self.activity.type)
        self.assertIn("title", result.data)
        self.assertIn("body", result.data)
        self.assertIn("url", result.data)
        self.assertIn("icon", result.data)

    def test_waiting_payment_activity_type(self):
        self.activity.type = Activity.TYPE_WAITING_PAYMENT
        serializer = ACTIVITY_NOTIFICATION_SERIALIZERS[self.activity.type]
        result = serializer(instance=self.activity)
        self.assertEqual(result.data.get("tag"), self.activity.type)
        self.assertIn("title", result.data)
        self.assertIn("body", result.data)
        self.assertIn("url", result.data)
        self.assertIn("icon", result.data)

    def test_group_coorganization_invite_activity_type(self):
        self.activity.type = Activity.TYPE_GROUP_COORGANIZATION_INVITE
        serializer = ACTIVITY_NOTIFICATION_SERIALIZERS[self.activity.type]
        result = serializer(instance=self.activity)
        self.assertEqual(result.data.get("tag"), self.activity.type)
        self.assertIn("title", result.data)
        self.assertIn("body", result.data)
        self.assertIn("url", result.data)
        self.assertIn("icon", result.data)

    def test_new_event_suggestion_activity_type(self):
        self.activity.type = Activity.TYPE_EVENT_SUGGESTION
        serializer = ACTIVITY_NOTIFICATION_SERIALIZERS[self.activity.type]
        result = serializer(instance=self.activity)
        self.assertEqual(result.data.get("tag"), self.activity.type)
        self.assertIn("title", result.data)
        self.assertIn("body", result.data)
        self.assertIn("url", result.data)
        self.assertIn("icon", result.data)

    def test_group_coorganization_info_activity_type(self):
        self.activity.type = Activity.TYPE_GROUP_COORGANIZATION_INFO
        serializer = ACTIVITY_NOTIFICATION_SERIALIZERS[self.activity.type]
        result = serializer(instance=self.activity)
        self.assertEqual(result.data.get("tag"), self.activity.type)
        self.assertIn("title", result.data)
        self.assertIn("body", result.data)
        self.assertIn("url", result.data)
        self.assertIn("icon", result.data)

    def test_new_message_activity_type(self):
        self.activity.type = Activity.TYPE_NEW_MESSAGE
        serializer = ACTIVITY_NOTIFICATION_SERIALIZERS[self.activity.type]
        result = serializer(instance=self.activity)
        self.assertEqual(result.data.get("tag"), self.activity.type)
        self.assertIn("title", result.data)
        self.assertIn("body", result.data)
        self.assertIn("url", result.data)
        self.assertIn("icon", result.data)

    def test_new_comment_activity_type(self):
        self.activity.type = Activity.TYPE_NEW_COMMENT
        serializer = ACTIVITY_NOTIFICATION_SERIALIZERS[self.activity.type]
        result = serializer(instance=self.activity)
        self.assertEqual(result.data.get("tag"), self.activity.type)
        self.assertIn("title", result.data)
        self.assertIn("body", result.data)
        self.assertIn("url", result.data)
        self.assertIn("icon", result.data)

    def test_new_comment_restricted_activity_type(self):
        self.activity.type = Activity.TYPE_NEW_COMMENT_RESTRICTED
        serializer = ACTIVITY_NOTIFICATION_SERIALIZERS[self.activity.type]
        result = serializer(instance=self.activity)
        self.assertEqual(result.data.get("tag"), self.activity.type)
        self.assertIn("title", result.data)
        self.assertIn("body", result.data)
        self.assertIn("url", result.data)
        self.assertIn("icon", result.data)

    def test_reminder_docs_event_eve_activity_type(self):
        self.activity.type = Activity.TYPE_REMINDER_DOCS_EVENT_EVE
        serializer = ACTIVITY_NOTIFICATION_SERIALIZERS[self.activity.type]
        result = serializer(instance=self.activity)
        self.assertEqual(result.data.get("tag"), self.activity.type)
        self.assertIn("title", result.data)
        self.assertIn("body", result.data)
        self.assertIn("url", result.data)
        self.assertIn("icon", result.data)

    def test_reminder_docs_event_nextday_activity_type(self):
        self.activity.type = Activity.TYPE_REMINDER_DOCS_EVENT_NEXTDAY
        serializer = ACTIVITY_NOTIFICATION_SERIALIZERS[self.activity.type]
        result = serializer(instance=self.activity)
        self.assertEqual(result.data.get("tag"), self.activity.type)
        self.assertIn("title", result.data)
        self.assertIn("body", result.data)
        self.assertIn("url", result.data)
        self.assertIn("icon", result.data)

    def test_reminder_report_form_for_event_activity_type(self):
        self.activity.type = Activity.TYPE_REMINDER_REPORT_FORM_FOR_EVENT
        serializer = ACTIVITY_NOTIFICATION_SERIALIZERS[self.activity.type]
        result = serializer(instance=self.activity)
        self.assertEqual(result.data.get("tag"), self.activity.type)
        self.assertIn("title", result.data)
        self.assertIn("body", result.data)
        self.assertIn("url", result.data)
        self.assertIn("icon", result.data)
