import logging

import pandas as pd

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.utils import timezone

from agir.donations.allocations import get_allocation_list
from agir.donations.apps import DonsConfig
from agir.donations.models import MonthlyAllocation
from agir.groups.models import SupportGroup
from agir.payments.models import Subscription
from agir.payments.payment_modes import PAYMENT_MODES
from agir.payments.types import SUBSCRIPTION_TYPES
from agir.system_pay import AbstractSystemPayPaymentMode

logger = logging.getLogger(__name__)


class SubscriptionException(Exception):
    pass


def create_subscription(person, mode, amount, allocations=None, **kwargs):
    from agir.payments.types import SUBSCRIPTION_TYPES

    subscription_type_id = kwargs.pop("type", DonsConfig.MONTHLY_DONATION_TYPE)
    subscription_type = SUBSCRIPTION_TYPES.get(subscription_type_id, None)
    day_of_month = kwargs.pop("day_of_month", settings.MONTHLY_DONATION_DAY)
    if (
        subscription_type
        and hasattr(subscription_type, "day_of_month")
        and isinstance(subscription_type.day_of_month, int)
    ):
        day_of_month = subscription_type.day_of_month

    subscription = Subscription.objects.create(
        person=person,
        price=amount,
        mode=mode,
        type=subscription_type_id,
        day_of_month=day_of_month,
        **kwargs,
    )

    if allocations is None:
        return subscription

    for allocation in get_allocation_list(allocations):
        group = allocation.pop("group", None)

        if group and not isinstance(group, SupportGroup):
            group = SupportGroup.objects.filter(pk=group).first()

        MonthlyAllocation.objects.create(
            **allocation,
            subscription=subscription,
            group=group,
        )

    return subscription


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
        try:
            context["expiry_date"] = subscription.system_pay_subscriptions.get(
                active=True
            ).alias.expiry_date
        except ObjectDoesNotExist:
            logger.error(
                f"No SystemPaySubscription found for subsciption #{subscription}",
                exc_info=True,
            )

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
    # attention à ne pas exécuter cette fonction dans une transaction !
    # il vaut mieux sauver au fur et à mesure les résultats de l'appel de cette fonction,
    # vu qu'elle peut interagir avec des systèmes externes.
    # Dans le cas contraire, il est très difficile d'identifier quelles opérations ont
    # effectivement été effectées.
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


def count_installments(subscription, start_date=None):
    if start_date is None:
        start_date = timezone.now().astimezone(timezone.get_default_timezone()).date()
    end_date = subscription.end_date

    if end_date is None:
        return None

    # compte le nombre de jours entre les deux dates limite dont le jour du mois est égal à la date de prélèvement
    days = pd.date_range(start=start_date, end=end_date, freq="D")
    return (days.day == subscription.day_of_month).sum()
