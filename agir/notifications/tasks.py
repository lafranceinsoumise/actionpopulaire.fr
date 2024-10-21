from push_notifications.apns import APNSServerError
from push_notifications.models import APNSDevice, GCMDevice

from agir.activity.models import Activity
from agir.lib.celery import http_task, gcm_push_task
from agir.notifications.serializers import ACTIVITY_NOTIFICATION_SERIALIZERS


@http_task(post_save=True)
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


@gcm_push_task(post_save=True)
def send_fcm_activity(activity_pk, fcm_device_pk):
    activity = Activity.objects.get(pk=activity_pk)
    fcm_device = GCMDevice.objects.get(pk=fcm_device_pk)
    serializer = ACTIVITY_NOTIFICATION_SERIALIZERS.get(activity.type, None)

    if serializer is None:
        return

    data = serializer(instance=activity).data
    data["image"] = data.pop("icon")

    # TODO disable for now, current GCM system is deprecated and fill the celery worker
    # return fcm_device.send_message(message=None, thread_id=activity.type, extra=data)
