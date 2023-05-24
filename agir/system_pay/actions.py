import logging

from agir.payments.actions.payments import (
    complete_payment,
    refuse_payment,
    refund_payment,
    notify_status_change,
)
from agir.payments.actions.subscriptions import (
    complete_subscription,
    terminate_subscription,
)
from agir.payments.models import Payment, Subscription
from agir.payments.payment_modes import PAYMENT_MODES
from agir.system_pay.models import SystemPayTransaction, SystemPaySubscription

logger = logging.getLogger(__name__)

SUBSCRIPTION_ERROR_STATUS_MAPPING = {
    SystemPayTransaction.STATUS_REFUSED: Subscription.STATUS_REFUSED,
    SystemPayTransaction.STATUS_ABANDONED: Subscription.STATUS_ABANDONED,
    SystemPayTransaction.STATUS_CANCELED: Subscription.STATUS_CANCELED,
}


def update_payment_from_transaction(payment, transaction):
    if transaction.status in (
        SystemPayTransaction.STATUS_CANCELED,
        SystemPayTransaction.STATUS_REFUNDED,
    ):
        refund_payment(payment)
    elif transaction.status == SystemPayTransaction.STATUS_COMPLETED:
        if payment.status == Payment.STATUS_CANCELED:
            logger.error(
                f"La transaction Systempay {transaction.pk} a été mise à jour alors que le paiement {payment.pk} était annulé"
            )
        elif transaction.is_refund:
            refund_payment(payment)
        else:
            complete_payment(payment)
    elif (
        transaction.status == SystemPayTransaction.STATUS_REFUSED
        and payment.status == Payment.STATUS_WAITING
    ):
        refuse_payment(payment)

    notify_status_change(payment)


def replace_sp_subscription_for_subscription(subscription, sp_subscription):
    for old_sp_subscription in SystemPaySubscription.objects.filter(
        subscription=subscription, active=True
    ).exclude(pk=sp_subscription.pk):
        # Ne pas annuler l'alias si on le réutilise pour la nouvelle souscription
        alias = old_sp_subscription.alias
        if alias != sp_subscription.alias:
            PAYMENT_MODES[subscription.mode].api_client.cancel_alias(alias)
            alias.active = False
            alias.save(update_fields=["active"])
        old_sp_subscription.active = False
        old_sp_subscription.save(update_fields=["active"])


def update_subscription_from_transaction(subscription, sp_transaction):
    if subscription.status == Subscription.STATUS_TERMINATED:
        logger.error(
            f"La transaction Systempay {sp_transaction.pk} a été mise à jour alors que l'abonnement {subscription.pk} était annulé"
        )
        return

    if sp_transaction.status == SystemPayTransaction.STATUS_COMPLETED:
        if subscription.status == Subscription.STATUS_CANCELED:
            # Peut arriver si nous annulons une souscription en attente, et que la personne la complète quand même.
            # Dans ce cas, il faut annuler la souscription côté SystemPay pour s'assurer qu'elle soit bien
            # correctement annulée. La souscription passera donc au du statut CANCELED au statut TERMINATED, puisqu'il y
            # aura bien eu complétion et création de la souscription systempay.
            # Il faut mettre son status temporairement à ACTIVE pour que 'terminate_subscription` ne lève pas une
            # exception.
            subscription.status = Subscription.STATUS_ACTIVE
            terminate_subscription(subscription)
            return

        complete_subscription(subscription)

    elif (
        subscription.status == SystemPayTransaction.STATUS_WAITING
        and sp_transaction.status in SUBSCRIPTION_ERROR_STATUS_MAPPING
    ):
        subscription.status = SUBSCRIPTION_ERROR_STATUS_MAPPING[sp_transaction.status]
        subscription.save()
