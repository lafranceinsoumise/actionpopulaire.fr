from django.core.exceptions import ObjectDoesNotExist
from push_notifications.models import APNSDevice, WebPushDevice, GCMDevice
from push_notifications.webpush import WebPushError
from push_notifications.apns import APNSServerError
from rest_framework.renderers import JSONRenderer

from agir.activity.models import Activity
from agir.lib.celery import http_task, post_save_task
from agir.notifications.serializers import ACTIVITY_NOTIFICATION_SERIALIZERS


@http_task
@post_save_task
def send_webpush_activity(activity_pk, webpush_device_pk):
    activity = Activity.objects.get(pk=activity_pk)
    webpush_device = WebPushDevice.objects.get(pk=webpush_device_pk)
    serializer = ACTIVITY_NOTIFICATION_SERIALIZERS.get(activity.type, None)

    if serializer is None:
        return

    message = serializer(instance=activity)
    message = JSONRenderer().render(message.data)

    try:
        result = webpush_device.send_message(message)
        if activity.push_status == Activity.STATUS_UNDISPLAYED:
            activity.push_status = Activity.STATUS_DISPLAYED
            activity.save()
        return result
    except WebPushError as e:
        if "Push failed: 410 Gone" in str(e):
            webpush_device.active = False
            webpush_device.save()
        elif "Push failed: 404 Not Found" in str(e):
            webpush_device.delete()
        else:
            raise e


@http_task
@post_save_task
def send_apns_activity(activity_pk, apns_device_pk):
    activity = Activity.objects.get(pk=activity_pk)
    apns_device = APNSDevice.objects.get(pk=apns_device_pk)
    serializer = ACTIVITY_NOTIFICATION_SERIALIZERS.get(activity.type, None)

    if serializer is None:
        return

    message = serializer(instance=activity)

    try:
        result = apns_device.send_message(
            message=message.data,
            thread_id=activity.type,
            extra={"url": message.data["url"]},
        )
    except APNSServerError as e:
        if "Unregistered" in str(e):
            apns_device.active = False
            apns_device.save()
            return
        else:
            raise e

    if activity.push_status == Activity.STATUS_UNDISPLAYED:
        activity.push_status = Activity.STATUS_DISPLAYED
        activity.save()
    return result


@http_task
@post_save_task
def send_fcm_activity(activity_pk, fcm_device_pk):
    activity = Activity.objects.get(pk=activity_pk)
    fcm_device = GCMDevice.objects.get(pk=fcm_device_pk)
    serializer = ACTIVITY_NOTIFICATION_SERIALIZERS.get(activity.type, None)

    if serializer is None:
        return

    data = serializer(instance=activity).data
    data["image"] = data.pop("icon")

    return fcm_device.send_message(message=None, thread_id=activity.type, extra=data)
