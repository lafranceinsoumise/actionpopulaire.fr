from django.db.models.signals import pre_delete
from django.dispatch import receiver

from agir.payments.actions import subscriptions
from agir.payments.models import Subscription
from agir.people.models import Person


@receiver(pre_delete, sender=Person, dispatch_uid="person_terminate_subscriptions")
def terminate_subscriptions(sender, instance, **kwargs):
    for subscription in instance.subscriptions.filter(
        status=Subscription.STATUS_ACTIVE
    ):
        # TODO: à faire dans une tâche Celery ?
        subscriptions.terminate_subscription(subscription)

    instance.subscriptions.filter(status=Subscription.STATUS_WAITING).update(
        status=Subscription.STATUS_ABANDONED
    )
