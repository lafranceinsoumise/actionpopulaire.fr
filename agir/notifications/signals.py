from django.db.models.signals import post_save
from django.dispatch import receiver

from push_notifications.models import WebPushDevice

from agir.activity.models import Activity
from agir.notifications.models import Subscription
from agir.notifications.tasks import send_webpush_activity


@receiver(post_save, sender=Activity, dispatch_uid="push_new_activity")
def push_new_activity(sender, instance, created, **kwargs):
    if (
        instance is None
        or not created
        or not Subscription.objects.filter(
            person=instance.recipient,
            type=Subscription.SUBSCRIPTION_PUSH,
            activity_type=instance.type,
        ).exists()
    ):
        return

    webpush_devices = [
        webpush_device.pk
        for webpush_device in WebPushDevice.objects.filter(
            user=instance.recipient.role, active=True
        )
    ]

    if len(webpush_devices) == 0:
        return

    send_webpush_activity.delay(instance.pk, webpush_devices)
