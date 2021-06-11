from django.db import migrations
from agir.notifications.actions import (
    DEFAULT_GROUP_SUBSCRIPTION_ACTIVITY_TYPES,
    DEFAULT_PERSON_SUBSCRIPTION_ACTIVITY_TYPES,
)


TYPE_GROUP_INVITATION = "group-invitation"
TYPE_NEW_MEMBER = "new-member"
TYPE_GROUP_MEMBERSHIP_LIMIT_REMINDER = "group-membership-limit-reminder"
TYPE_GROUP_INFO_UPDATE = "group-info-update"
TYPE_NEW_ATTENDEE = "new-attendee"
TYPE_EVENT_UPDATE = "event-update"
TYPE_NEW_EVENT_MYGROUPS = "new-event-mygroups"
TYPE_NEW_MESSAGE = "new-message"
TYPE_NEW_COMMENT = "new-comment"
TYPE_NEW_REPORT = "new-report"
TYPE_CANCELLED_EVENT = "cancelled-event"
TYPE_REFERRAL = "referral-accepted"
TYPE_GROUP_CREATION_CONFIRMATION = "group-creation-confirmation"
TYPE_ACCEPTED_INVITATION_MEMBER = "accepted-invitation-member"
TYPE_TRANSFERRED_GROUP_MEMBER = "transferred-group-member"
TYPE_NEW_MEMBERS_THROUGH_TRANSFER = "new-members-through-transfer"
TYPE_WAITING_LOCATION_EVENT = "waiting-location-event"
TYPE_WAITING_LOCATION_GROUP = "waiting-location-group"
TYPE_EVENT_SUGGESTION = "event-suggestion"
TYPE_ANNOUNCEMENT = "announcement"
TYPE_GROUP_COORGANIZATION_INFO = "group-coorganization-info"
TYPE_GROUP_COORGANIZATION_ACCEPTED = "group-coorganization-accepted"
TYPE_GROUP_COORGANIZATION_INVITE = "group-coorganization-invite"
TYPE_WAITING_PAYMENT = "waiting-payment"

SUBSCRIPTION_EMAIL = "email"
SUBSCRIPTION_PUSH = "push"


def migrate_default_subscriptions_switch_global_notifications_enabled(
    apps, schema_editor
):
    Subscription = apps.get_model("notifications", "Subscription")
    Person = apps.get_model("people", "Person")

    # Add general email subscriptions
    Subscription.objects.bulk_create(
        [
            Subscription(person=p, type=SUBSCRIPTION_EMAIL, activity_type=t,)
            for p in Person.objects.all()
            for t in [
                # GENERAL
                TYPE_TRANSFERRED_GROUP_MEMBER,
                TYPE_GROUP_INVITATION,
            ]
        ]
    )

    # If 'event_notifications' or 'group_notifications' are set, add or remove their subscriptions

    # Events : add default subscriptions if notifications_event_enabled=True
    Subscription.objects.bulk_create(
        [
            Subscription(person=p, type=SUBSCRIPTION_EMAIL, activity_type=t,)
            for p in Person.objects.all().filter(event_notifications=True)
            for t in [
                # EVENTS
                TYPE_EVENT_UPDATE,
                TYPE_EVENT_SUGGESTION,
                TYPE_NEW_ATTENDEE,
                TYPE_WAITING_LOCATION_EVENT,
            ]
        ]
    )
    # Groups : delete default subscription (auto-created for groups) if notifications_group_enabled=False
    for s in Subscription.objects.filter(type=SUBSCRIPTION_EMAIL):
        if (
            s.person.group_notifications is False
            or s.membership.group_notifications is False
        ) and s.activity_type in DEFAULT_GROUP_SUBSCRIPTION_ACTIVITY_TYPES:
            s.delete()


def reverse_subscriptions_migrations(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("people", "0004_display_name_and_image"),
    ]

    operations = [
        migrations.RunPython(
            migrate_default_subscriptions_switch_global_notifications_enabled,
            reverse_subscriptions_migrations,
            atomic=True,
        ),
    ]
