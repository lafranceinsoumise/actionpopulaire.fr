from django.db import transaction
from django.http import HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.utils import timezone

from agir.payments.models import Subscription
from agir.payments.payment_modes import DEFAULT_MODE, PAYMENT_MODES
from agir.payments.types import SUBSCRIPTION_TYPES
from agir.system_pay import AbstractSystemPayPaymentMode


class SubscriptionException(Exception):
    pass


def create_subscription(person, type, price, mode=DEFAULT_MODE, **kwargs):
    return Subscription.objects.create(
        person=person, price=price, mode=mode, type=type, **kwargs
    )


def redirect_to_subscribe(subscription):
    return HttpResponseRedirect(reverse("subscription_page", args=[subscription.pk]))


def complete_subscription(subscription):
    if subscription.status in (
        Subscription.STATUS_CANCELED,
        Subscription.STATUS_TERMINATED,
    ):
        raise SubscriptionException("L'abonnement a déjà été annulé.")

    subscription.status = Subscription.STATUS_ACTIVE
    subscription.save()


def notify_status_change(subscription):
    # call the registered listener for this event type if there is one to notify it of the changes in status
    if (
        subscription.type in SUBSCRIPTION_TYPES
        and SUBSCRIPTION_TYPES[subscription.type].status_listener
    ):
        SUBSCRIPTION_TYPES[subscription.type].status_listener(subscription)


def terminate_subscription(subscription):
    if subscription.status != Subscription.STATUS_ACTIVE:
        raise SubscriptionException("Impossible de mettre fin un abonnement non actif.")

    with transaction.atomic():
        PAYMENT_MODES[subscription.mode].subscription_terminate_action(subscription)

        subscription.status = Subscription.STATUS_TERMINATED
        subscription.end_date = timezone.now()
        subscription.save(update_fields=["status"])


def default_description_context_generator(subscription):
    subscription_type = SUBSCRIPTION_TYPES[subscription.type]
    context = {"subscription": subscription, "subscription_type": subscription_type}

    if isinstance(PAYMENT_MODES[subscription.mode], AbstractSystemPayPaymentMode):
        context["expiry_date"] = subscription.system_pay_subscriptions.get(
            active=True
        ).alias.expiry_date

    return context


def description_for_subscription(subscription):
    if subscription.type not in SUBSCRIPTION_TYPES:
        raise SubscriptionException("Le type n'existe pas")

    subscription_type = SUBSCRIPTION_TYPES[subscription.type]
    template_name = subscription_type.description_template
    context_generator = (
        subscription_type.description_context_generator
        or default_description_context_generator
    )

    return loader.render_to_string(template_name, context_generator(subscription))


def replace_subscription(previous_subscription, new_subscription):
    assert previous_subscription.mode == new_subscription.mode
    assert previous_subscription.status == Subscription.STATUS_ACTIVE
    assert new_subscription.status == Subscription.STATUS_WAITING

    PAYMENT_MODES[previous_subscription.mode].subscription_replace_action(
        previous_subscription, new_subscription
    )

    previous_subscription.status = Subscription.STATUS_TERMINATED
    new_subscription.status = Subscription.STATUS_ACTIVE
    previous_subscription.save(update_fields=["status"])
    new_subscription.save(update_fields=["status"])
