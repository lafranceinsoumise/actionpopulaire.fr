from django.db import migrations, models
from django.db.models import Q

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
    Activity = apps.get_model("activity", "Activity")
    Subscription = apps.get_model("notifications", "Subscription")
    Person = apps.get_model("people", "Person")

    # ALL SUBSCRIPTIONS EMAIL
    Subscription.objects.bulk_create(
        [
            Subscription(person=p, type=SUBSCRIPTION_EMAIL, activity_type=t,)
            for p in Person.objects.all()
            for t in [
                # GENERAL
                TYPE_REFERRAL,
                TYPE_TRANSFERRED_GROUP_MEMBER,
                TYPE_GROUP_INVITATION,
                TYPE_WAITING_PAYMENT,
            ]
        ]
    )
    # EVENTS : add default subscriptions if notifications_event_enabled=True
    Subscription.objects.bulk_create(
        [
            Subscription(person=p, type=SUBSCRIPTION_EMAIL, activity_type=t,)
            for p in Person.objects.all().filter(event_notifications=True)
            for t in [
                # EVENTS
                TYPE_EVENT_UPDATE,
                TYPE_NEW_ATTENDEE,
                TYPE_EVENT_SUGGESTION,
                TYPE_WAITING_LOCATION_EVENT,
            ]
        ]
    )
    # GROUPS : delete default subscription (auto-created for groups) if notifications_group_enabled=False
    for s in Subscription.objects.filter(type=SUBSCRIPTION_EMAIL):
        if (
            s.person.group_notifications is False
            or s.membership.group_notifications is False
        ) and s.activity_type in [
            # GROUPS
            TYPE_NEW_EVENT_MYGROUPS,
            TYPE_NEW_REPORT,
            TYPE_GROUP_INFO_UPDATE,
            TYPE_NEW_MESSAGE,
            TYPE_NEW_COMMENT,
            TYPE_NEW_MEMBER,
            TYPE_ACCEPTED_INVITATION_MEMBER,
            TYPE_GROUP_MEMBERSHIP_LIMIT_REMINDER,
            TYPE_NEW_MEMBERS_THROUGH_TRANSFER,
            TYPE_WAITING_LOCATION_GROUP,
            TYPE_GROUP_COORGANIZATION_INVITE,
        ]:
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
