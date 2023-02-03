import json

from django.db.models.signals import post_save
from django.dispatch import receiver

from agir.activity.models import Activity
from agir.event_requests.models import EventSpeakerRequest


@receiver(
    post_save,
    sender=EventSpeakerRequest,
    dispatch_uid="create_new_event_speaker_request_activity",
)
def create_new_event_speaker_request_activity(
    sender, instance, created=False, **kwargs
):
    if instance is None or not created:
        return

    activity_meta = json.dumps({"event_request_id": str(instance.event_request_id)})

    Activity.objects.get_or_create(
        type=Activity.TYPE_NEW_EVENT_SPEAKER_REQUEST,
        recipient_id=instance.event_speaker.person_id,
        meta=activity_meta,
    )
