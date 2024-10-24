from push_notifications.models import GCMDevice

from agir.activity.models import Activity
from agir.lib.celery import gcm_push_task
from agir.notifications.serializers import ACTIVITY_NOTIFICATION_SERIALIZERS
from firebase_admin import messaging


@gcm_push_task(post_save=True)
def send_fcm_activity(activity_pk, fcm_device_pk):
    activity = Activity.objects.get(pk=activity_pk)
    fcm_device = GCMDevice.objects.get(pk=fcm_device_pk)
    serializer = ACTIVITY_NOTIFICATION_SERIALIZERS.get(activity.type, None)

    if serializer is None:
        return

    data = serializer(instance=activity).data

    fcm_message = messaging.Message(
        data={"url": data["url"]},
        notification=messaging.Notification(
            title=data["title"],
            image=data["image"] if "image" in data else data["icon"],
            body=data["body"],
        ),
    )

    return fcm_device.send_message(fcm_message)
