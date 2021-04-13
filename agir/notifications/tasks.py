from django.core.exceptions import ObjectDoesNotExist
from push_notifications.models import APNSDevice, WebPushDevice
from push_notifications.webpush import WebPushError
from rest_framework.renderers import JSONRenderer

from agir.activity.models import Activity
from agir.lib.celery import http_task
from agir.notifications.serializers import ACTIVITY_NOTIFICATION_SERIALIZERS


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


@http_task
def send_apns_activity(activity_pk, apns_device_pk):
    try:
        activity = Activity.objects.get(pk=activity_pk)
    except ObjectDoesNotExist:
        return

    try:
        apns_device = APNSDevice.objects.get(pk=apns_device_pk)
    except ObjectDoesNotExist:
        return

    serializer = ACTIVITY_NOTIFICATION_SERIALIZERS.get(activity.type, None)

    if serializer is None:
        return

    message = serializer(instance=activity)

    return apns_device.send_message(message=message.data, thread_id=activity.type)
