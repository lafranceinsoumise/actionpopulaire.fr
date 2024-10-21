from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from functools import partial

from push_notifications.models import APNSDevice, GCMDevice, WebPushDevice

from agir.activity.models import Activity
from agir.groups.models import Membership
from agir.notifications.actions import (
    create_default_group_membership_subscriptions,
    create_default_person_push_subscriptions,
    create_default_person_email_subscriptions,
)
from agir.notifications.models import Subscription
from agir.notifications.tasks import (
    send_apns_activity,
    send_fcm_activity,
)
from agir.people.models import Person


@receiver(post_save, sender=Activity, dispatch_uid="push_new_activity")
def push_new_activity(sender, instance, created=False, **kwargs):
    if instance is None or not created:
        return

    if (
        not instance.type in Subscription.MANDATORY_PUSH_TYPES
        and not Subscription.objects.filter(
            person=instance.recipient,
            type=Subscription.SUBSCRIPTION_PUSH,
            activity_type=instance.type,
        ).exists()
    ):
        return

    # SEND APPLE PUSH NOTIFICATION SERVICE NOTIFICATIONS
    apns_device_pks = [
        apns_device.pk
        for apns_device in APNSDevice.objects.filter(
            user=instance.recipient.role, active=True
        )
    ]

    for apns_device_pk in apns_device_pks:
        send_apns_activity.delay(
            instance.pk,
            apns_device_pk,
        )


@receiver(
    post_save,
    sender=APNSDevice,
    dispatch_uid="create_default_person_subscriptions__apns",
)
@receiver(
    post_save,
    sender=GCMDevice,
    dispatch_uid="create_default_person_subscriptions__fcm",
)
def push_device_post_save_handler(sender, instance, created=False, **kwargs):
    is_first_device = (
        instance is not None
        and created is True
        and not Subscription.objects.filter(person=instance.user.person).exists()
        and APNSDevice.objects.filter(user=instance.user).count()
        + GCMDevice.objects.filter(user=instance.user).count()
        + WebPushDevice.objects.filter(user=instance.user).count()
        == 1
    )

    if is_first_device:
        create_default_person_push_subscriptions(instance.user.person)


@receiver(
    post_save,
    sender=GCMDevice,
    dispatch_uid="create_default_person_subscriptions__fcm",
)
def fcm_device_replace_webpush(sender, instance, created=False, **kwargs):
    if instance is not None and created is True:
        WebPushDevice.objects.filter(user=instance.user).update(active=False)


@receiver(
    post_save, sender=Membership, dispatch_uid="create_default_membership_subscriptions"
)
def membership_post_save_handler(sender, instance, created=False, **kwargs):
    if (
        instance is None
        or not created
        or not instance.default_subscriptions_enabled
        or instance.subscription_set.count() > 0
    ):
        return

    create_default_group_membership_subscriptions(instance.person, instance)


@receiver(
    post_save, sender=Person, dispatch_uid="create_default_person_email_subscriptions"
)
def person_post_save_handler(sender, instance, created=False, **kwargs):
    if (
        instance is None
        or not created
        or Subscription.objects.filter(
            person=instance,
            type=Subscription.SUBSCRIPTION_EMAIL,
            activity_type__in=Subscription.DEFAULT_PERSON_EMAIL_TYPES,
        ).exists()
    ):
        return

    create_default_person_email_subscriptions(instance)
