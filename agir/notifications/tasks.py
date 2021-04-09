from django.core.exceptions import ObjectDoesNotExist
from push_notifications.models import WebPushDevice

from agir.activity.models import Activity
from agir.lib.celery import http_task
from agir.notifications.actions import send_webpush_activity_notifications


@http_task
def send_webpush_activity(activity_pk, webpush_device_pk):
    try:
        activity = Activity.objects.get(pk=activity_pk)
    except ObjectDoesNotExist:
        return

    try:
        webpush_device = WebPushDevice.objects.get(pk=webpush_device_pk)
    except ObjectDoesNotExist:
        return

    send_webpush_activity_notifications(activity, webpush_device)
