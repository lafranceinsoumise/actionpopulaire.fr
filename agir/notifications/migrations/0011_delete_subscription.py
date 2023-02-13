from django.db import migrations

SUBSCRIPTION_EMAIL = "email"
SUBSCRIPTION_PUSH = "push"

# PERSON/EVENT TYPES
TYPE_NEW_ATTENDEE = "new-attendee"
TYPE_EVENT_UPDATE = "event-update"
TYPE_CANCELLED_EVENT = "cancelled-event"
TYPE_WAITING_LOCATION_EVENT = "waiting-location-event"
TYPE_WAITING_LOCATION_GROUP = "waiting-location-group"
TYPE_EVENT_SUGGESTION = "event-suggestion"
TYPE_ANNOUNCEMENT = "announcement"

# DEFAULT PERSON/EVENT TYPES
DEFAULT_PERSON_EMAIL_TYPES = [
    TYPE_EVENT_SUGGESTION,
    TYPE_EVENT_UPDATE,
    TYPE_NEW_ATTENDEE,
    TYPE_WAITING_LOCATION_EVENT,
]


def delete_event_subscriptions_disabled(apps, schema_editor):
    Subscription = apps.get_model("notifications", "Subscription")

    Subscription.objects.filter(
        type=SUBSCRIPTION_EMAIL,
        activity_type__in=DEFAULT_PERSON_EMAIL_TYPES,
        person__event_notifications=False,
    ).delete()


def reverse_deletion(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("notifications", "0010_migrate_types"),
    ]

    operations = [
        migrations.RunPython(
            delete_event_subscriptions_disabled,
            reverse_deletion,
            atomic=True,
        ),
    ]
