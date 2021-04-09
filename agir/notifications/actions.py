from rest_framework.renderers import JSONRenderer

from push_notifications.webpush import WebPushError

from agir.notifications.serializers import ACTIVITY_NOTIFICATION_SERIALIZERS


def send_webpush_activity_notifications(activity, webpush_device):
    serializer = ACTIVITY_NOTIFICATION_SERIALIZERS.get(activity.type, None)

    if serializer is None:
        return

    message = serializer(instance=activity)
    message = JSONRenderer().render(message.data)

    try:
        return webpush_device.send_message(message)
    except WebPushError as e:
        if "Push failed: 410 Gone" in str(e):
            webpush_device.active = False
            webpush_device.save()
