from django.db import migrations

SUBSCRIPTION_EMAIL = "email"
SUBSCRIPTION_PUSH = "push"

TYPE_REFERRAL = "referral-accepted"

# PERSON/EVENT TYPES
TYPE_NEW_ATTENDEE = "new-attendee"
TYPE_EVENT_UPDATE = "event-update"
TYPE_CANCELLED_EVENT = "cancelled-event"
TYPE_WAITING_LOCATION_EVENT = "waiting-location-event"
TYPE_WAITING_LOCATION_GROUP = "waiting-location-group"
TYPE_EVENT_SUGGESTION = "event-suggestion"
TYPE_ANNOUNCEMENT = "announcement"

# GROUP TYPES
TYPE_NEW_REPORT = "new-report"
TYPE_NEW_EVENT_MYGROUPS = "new-event-mygroups"
TYPE_GROUP_INVITATION = "group-invitation"
TYPE_NEW_MEMBER = "new-member"
TYPE_GROUP_MEMBERSHIP_LIMIT_REMINDER = "group-membership-limit-reminder"
TYPE_GROUP_INFO_UPDATE = "group-info-update"
TYPE_NEW_MESSAGE = "new-message"
TYPE_NEW_COMMENT = "new-comment"
TYPE_GROUP_CREATION_CONFIRMATION = "group-creation-confirmation"
TYPE_ACCEPTED_INVITATION_MEMBER = "accepted-invitation-member"
TYPE_TRANSFERRED_GROUP_MEMBER = "transferred-group-member"
TYPE_NEW_MEMBERS_THROUGH_TRANSFER = "new-members-through-transfer"

# OTHER
TYPE_GROUP_COORGANIZATION_INFO = "group-coorganization-info"
TYPE_GROUP_COORGANIZATION_ACCEPTED = "group-coorganization-accepted"
TYPE_GROUP_COORGANIZATION_INVITE = "group-coorganization-invite"
TYPE_WAITING_PAYMENT = "waiting-payment"

# MANDATORY TYPES
MANDATORY_EMAIL_TYPES = (
    TYPE_WAITING_PAYMENT,
    # EVENT
    TYPE_CANCELLED_EVENT,
    # GROUP
    TYPE_TRANSFERRED_GROUP_MEMBER,
    TYPE_GROUP_INVITATION,
    TYPE_GROUP_MEMBERSHIP_LIMIT_REMINDER,
)

# DEFAULT PERSON/EVENT TYPES
DEFAULT_PERSON_EMAIL_TYPES = [
    TYPE_EVENT_SUGGESTION,
    TYPE_EVENT_UPDATE,
    TYPE_NEW_ATTENDEE,
    TYPE_WAITING_LOCATION_EVENT,
]

# DEFAULT GROUP TYPES
DEFAULT_GROUP_EMAIL_TYPES = [
    TYPE_NEW_EVENT_MYGROUPS,
    TYPE_GROUP_COORGANIZATION_INFO,
    TYPE_GROUP_INFO_UPDATE,
    TYPE_NEW_MESSAGE,
    TYPE_NEW_COMMENT,
    TYPE_NEW_REPORT,
    TYPE_NEW_MEMBER,
    TYPE_ACCEPTED_INVITATION_MEMBER,
    TYPE_NEW_MEMBERS_THROUGH_TRANSFER,
    TYPE_WAITING_LOCATION_GROUP,
    TYPE_GROUP_COORGANIZATION_INVITE,
    TYPE_GROUP_CREATION_CONFIRMATION,
    TYPE_GROUP_COORGANIZATION_ACCEPTED,
]


def migrate_default_subscriptions_switch_global_notifications_enabled(
    apps, schema_editor
):
    Subscription = apps.get_model("notifications", "Subscription")
    Person = apps.get_model("people", "Person")

    # Delete mandatory subscriptions for push and email (here MANDATORY_EMAIL_TYPES = MANDATORY_PUSH_TYPES)
    Subscription.objects.filter(activity_type__in=MANDATORY_EMAIL_TYPES).delete()

    # If 'event_notifications' or 'group_notifications' are set, add or remove their subscriptions :

    # Events : add default subscriptions if notifications_event_enabled=True
    Subscription.objects.bulk_create(
        [
            Subscription(person=p, type=SUBSCRIPTION_EMAIL, activity_type=t,)
            for p in Person.objects.all().filter(event_notifications=True)
            for t in DEFAULT_PERSON_EMAIL_TYPES
        ]
    )
    Subscription.objects.bulk_create(
        [
            Subscription(person=p, type=SUBSCRIPTION_PUSH, activity_type=t,)
            for p in Person.objects.all().filter(event_notifications=True)
            for t in DEFAULT_PERSON_EMAIL_TYPES
        ]
    )

    # Groups : delete default subscription (auto-created for groups) if notifications_group_enabled=False
    for s in Subscription.objects.all():
        if (
            s.person.group_notifications is False
            or s.membership.group_notifications is False
        ) and s.activity_type in DEFAULT_GROUP_EMAIL_TYPES:
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
