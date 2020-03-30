from django.conf import settings
from django.db import transaction
from django.db.models.signals import post_save, pre_delete, post_delete
from django.dispatch import receiver
from functools import partial

from agir.payments.actions import subscriptions
from . import tasks
from .models import Person, PersonEmail
from ..payments.models import Subscription


@receiver(post_save, sender=Person, dispatch_uid="person_update_mailtrain")
def update_mailtrain(sender, instance, raw, **kwargs):
    if settings.MAILTRAIN_DISABLE:
        return

    if kwargs["created"]:
        return

    transaction.on_commit(partial(tasks.update_person_mailtrain.delay, instance.id))


@receiver(pre_delete, sender=Person, dispatch_uid="person_delete_mailtrain")
def delete_mailtrain(sender, instance, **kwargs):
    if instance.email:
        tasks.delete_email_mailtrain.delay(instance.email)


@receiver(pre_delete, sender=Person, dispatch_uid="person_terminate_subscriptions")
def terminate_subscriptions(sender, instance, **kwargs):
    for subscription in instance.subscriptions.exclude(
        status=Subscription.STATUS_TERMINATED
    ):
        # TODO: à faire dans une tâche Celery ?
        # we get a 500 if some remove their account with a waiting subscription, but that should not happen
        subscriptions.terminate_subscription(subscription)


@receiver(post_delete, sender=Person, dispatch_uid="person_delete_role")
def delete_role(sender, instance, **kwargs):
    if instance.role is not None:
        instance.role.delete()


@receiver(post_delete, sender=PersonEmail, dispatch_uid="personemail_delete_mailtrain")
def delete_email_person(sender, instance, **kwargs):
    if settings.MAILTRAIN_DISABLE:
        return

    try:
        tasks.delete_email_mailtrain.delay(instance.address)
    except Person.DoesNotExist:
        pass
