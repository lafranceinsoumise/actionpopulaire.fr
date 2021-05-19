from django.db import transaction

from agir.activity.models import Activity


@transaction.atomic()
def new_event_suggestion_notification(event, recipient):
    activity_config = {
        "type": Activity.TYPE_EVENT_SUGGESTION,
        "event": event,
        "status": Activity.DISPLAYED_TYPES,
    }
    if event.organizers_groups.count() > 0:
        activity_config["supportgroup"] = event.organizers_groups.first()
    else:
        activity_config["individual"] = event.organizers.first()

    Activity.objects.bulk_create(
        [Activity(**activity_config, recipient=recipient)], send_post_save_signal=True,
    )
