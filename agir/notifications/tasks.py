from agir.activity.models import Activity
from agir.lib.celery import http_task
from agir.notifications.actions import send_activity_notifications


@http_task
def send_webpush_activity(activity_pk, device_pks):
    try:
        activity = Activity.objects.get(pk=activity_pk)
    except Activity.DoesNotExist:
        return

    send_activity_notifications(activity)
