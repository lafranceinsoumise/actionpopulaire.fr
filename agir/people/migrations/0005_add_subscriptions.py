from django.db import migrations
from agir.notifications.types import SubscriptionType

SUBSCRIPTION_EMAIL = "email"
SUBSCRIPTION_PUSH = "push"


def migrate_default_subscriptions_switch_global_notifications_enabled(
    apps, schema_editor
):
    Subscription = apps.get_model("notifications", "Subscription")
    Person = apps.get_model("people", "Person")

    # Delete mandatory subscriptions for push and email (here MANDATORY_EMAIL_TYPES = MANDATORY_PUSH_TYPES)
    Subscription.objects.filter(
        activity_type__in=SubscriptionType.MANDATORY_EMAIL_TYPES
    ).delete()

    # If 'event_notifications' or 'group_notifications' are set, add or remove their subscriptions :

    # Events : add default subscriptions if notifications_event_enabled=True
    Subscription.objects.bulk_create(
        [
            Subscription(person=p, type=SUBSCRIPTION_EMAIL, activity_type=t,)
            for p in Person.objects.all().filter(event_notifications=True)
            for t in [
                # EVENTS
                SubscriptionType.TYPE_EVENT_UPDATE,
                SubscriptionType.TYPE_EVENT_SUGGESTION,
                SubscriptionType.TYPE_NEW_ATTENDEE,
                SubscriptionType.TYPE_WAITING_LOCATION_EVENT,
            ]
        ]
    )
    # Groups : delete default subscription (auto-created for groups) if notifications_group_enabled=False
    for s in Subscription.objects.filter(type=SUBSCRIPTION_EMAIL):
        if (
            s.person.group_notifications is False
            or s.membership.group_notifications is False
        ) and s.activity_type in SubscriptionType.DEFAULT_GROUP_EMAIL_TYPES:
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
