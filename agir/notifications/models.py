from django.db import models

from agir.activity.models import Activity
from agir.people.models import Person
from agir.lib.models import TimeStampedModel, UUIDIdentified


class Subscription(UUIDIdentified, TimeStampedModel):
    SUBSCRIPTION_EMAIL = "email"
    SUBSCRIPTION_PUSH = "push"
    SUBSCRIPTION_CHOICES = (
        (SUBSCRIPTION_EMAIL, "Email"),
        (SUBSCRIPTION_PUSH, "Push"),
    )

    # MANDATORY TYPES
    MANDATORY_EMAIL_TYPES = (
        Activity.TYPE_WAITING_PAYMENT,
        # EVENT
        Activity.TYPE_CANCELLED_EVENT,
        Activity.TYPE_REMINDER_DOCS_EVENT_EVE,
        Activity.TYPE_REMINDER_DOCS_EVENT_NEXTDAY,
        Activity.TYPE_REMINDER_REPORT_FORM_FOR_EVENT,
        # GROUP
        Activity.TYPE_TRANSFERRED_GROUP_MEMBER,
        Activity.TYPE_GROUP_INVITATION,
        Activity.TYPE_GROUP_MEMBERSHIP_LIMIT_REMINDER,
        Activity.TYPE_UNCERTIFIABLE_GROUP_WARNING,
    )
    MANDATORY_PUSH_TYPES = (
        Activity.TYPE_PUSH_ANNOUNCEMENT,
        Activity.TYPE_WAITING_PAYMENT,
        # EVENT
        Activity.TYPE_CANCELLED_EVENT,
        Activity.TYPE_REMINDER_REPORT_FORM_FOR_EVENT,
        # GROUP
        Activity.TYPE_TRANSFERRED_GROUP_MEMBER,
        Activity.TYPE_GROUP_INVITATION,
        Activity.TYPE_GROUP_MEMBERSHIP_LIMIT_REMINDER,
    )

    # DEFAULT PERSON/EVENT TYPES
    DEFAULT_PERSON_EMAIL_TYPES = [
        Activity.TYPE_EVENT_SUGGESTION,
        Activity.TYPE_EVENT_UPDATE,
        Activity.TYPE_NEW_ATTENDEE,
        Activity.TYPE_NEW_GROUP_ATTENDEE,
        Activity.TYPE_WAITING_LOCATION_EVENT,
    ]
    DEFAULT_PERSON_PUSH_TYPES = [
        Activity.TYPE_EVENT_SUGGESTION,
        Activity.TYPE_EVENT_UPDATE,
        Activity.TYPE_NEW_ATTENDEE,
        Activity.TYPE_NEW_GROUP_ATTENDEE,
        Activity.TYPE_WAITING_LOCATION_EVENT,
        Activity.TYPE_REMINDER_DOCS_EVENT_EVE,
        Activity.TYPE_REMINDER_DOCS_EVENT_NEXTDAY,
        Activity.TYPE_REMINDER_UPCOMING_EVENT_START,
    ]

    # DEFAULT GROUP TYPES
    DEFAULT_GROUP_EMAIL_TYPES = [
        Activity.TYPE_NEW_EVENT_MYGROUPS,
        Activity.TYPE_GROUP_COORGANIZATION_INFO,
        Activity.TYPE_GROUP_INFO_UPDATE,
        Activity.TYPE_NEW_MESSAGE,
        Activity.TYPE_NEW_COMMENT,
        Activity.TYPE_NEW_COMMENT_RESTRICTED,
        Activity.TYPE_NEW_REPORT,
        Activity.TYPE_NEW_MEMBER,
        Activity.TYPE_ACCEPTED_INVITATION_MEMBER,
        Activity.TYPE_NEW_MEMBERS_THROUGH_TRANSFER,
        Activity.TYPE_WAITING_LOCATION_GROUP,
        Activity.TYPE_GROUP_CREATION_CONFIRMATION,
        Activity.TYPE_GROUP_COORGANIZATION_INVITE,
        Activity.TYPE_GROUP_COORGANIZATION_ACCEPTED,
    ]
    DEFAULT_GROUP_PUSH_TYPES = [
        Activity.TYPE_NEW_EVENT_MYGROUPS,
        Activity.TYPE_GROUP_COORGANIZATION_INFO,
        Activity.TYPE_GROUP_INFO_UPDATE,
        Activity.TYPE_NEW_MESSAGE,
        Activity.TYPE_NEW_COMMENT,
        Activity.TYPE_NEW_COMMENT_RESTRICTED,
        Activity.TYPE_NEW_REPORT,
        Activity.TYPE_NEW_FOLLOWER,
        Activity.TYPE_NEW_MEMBER,
        Activity.TYPE_ACCEPTED_INVITATION_MEMBER,
        Activity.TYPE_NEW_MEMBERS_THROUGH_TRANSFER,
        Activity.TYPE_WAITING_LOCATION_GROUP,
        Activity.TYPE_GROUP_CREATION_CONFIRMATION,
        Activity.TYPE_GROUP_COORGANIZATION_INVITE,
        Activity.TYPE_GROUP_COORGANIZATION_ACCEPTED,
    ]

    person = models.ForeignKey(
        "people.Person",
        on_delete=models.CASCADE,
        related_name="notification_subscriptions",
    )
    membership = models.ForeignKey(
        "groups.Membership", on_delete=models.CASCADE, null=True
    )
    type = models.CharField("Type", max_length=5, choices=SUBSCRIPTION_CHOICES)
    activity_type = models.CharField(
        "Type", max_length=50, choices=Activity.TYPE_CHOICES
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["person", "type", "activity_type", "membership"],
                name="unique_with_membership",
            ),
            models.UniqueConstraint(
                fields=["person", "type", "activity_type"],
                condition=models.Q(membership=None),
                name="unique_without_membership",
            ),
        ]
