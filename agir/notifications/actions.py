from pywebpush import WebPushException

from agir.notifications.models import WebPushDevice


def send_activity_notifications(activity):
    for web_push_device in WebPushDevice.objects.filter(
        user=activity.recipient.role, subscriptions__type=activity.type
    ):
        try:
            return web_push_device.send_message(f"activity:{activity.pk}")
        except WebPushException as e:
            if e.response.status_code == 410:
                web_push_device.subscriptions.all().delete()
                web_push_device.delete()
