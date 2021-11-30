from django.db import transaction

from agir.activity.models import Activity
from agir.events.models import Event


@transaction.atomic()
def new_event_suggestion_notification(event, recipient):
    activity_config = {
        "type": Activity.TYPE_EVENT_SUGGESTION,
        "event": event,
    }
    if event.organizers_groups.count() > 0:
        activity_config["supportgroup"] = event.organizers_groups.first()
    else:
        activity_config["individual"] = event.organizers.first()

    Activity.objects.create(
        **activity_config,
        recipient=recipient,
    )


@transaction.atomic()
def event_required_document_reminder_notification(event_pk, post=False, pre=False):
    activity_type = None
    if post:
        activity_type = Activity.TYPE_REMINDER_DOCS_EVENT_EVE
    elif pre:
        activity_type = Activity.TYPE_REMINDER_DOCS_EVENT_NEXTDAY
    if activity_type is None:
        return

    try:
        event = Event.objects.get(pk=event_pk)
    except Event.DoesNotExist:
        return

    Activity.objects.bulk_create(
        [
            Activity(
                type=activity_type,
                recipient=organizer,
                event=event,
            )
            for organizer in event.organizers.all()
        ],
        send_post_save_signal=True,
    )
