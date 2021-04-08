from rest_framework.renderers import JSONRenderer

from push_notifications.models import WebPushDevice
from push_notifications.webpush import WebPushError

from agir.notifications.serializers import ACTIVITY_NOTIFICATION_SERIALIZERS


def send_activity_notifications(activity):
    serializer = ACTIVITY_NOTIFICATION_SERIALIZERS.get(activity.type, None)
    if serializer is None:
        return
    message = serializer(instance=activity)
    message = JSONRenderer().render(message.data)

    for web_push_device in WebPushDevice.objects.filter(
        user=activity.recipient.role, active=True
    ):
        try:
            return web_push_device.send_message(message)
        except WebPushError as e:
            if "Push failed: 410 Gone" in str(e):
                web_push_device.active = False
                web_push_device.save()
