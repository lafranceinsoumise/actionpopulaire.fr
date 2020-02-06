import logging

from agir.payments.actions.payments import (
    complete_payment,
    refuse_payment,
    refund_payment,
)
from agir.payments.actions.subscriptions import complete_subscription
from agir.payments.models import Payment, Subscription
from agir.payments.payment_modes import PAYMENT_MODES
from agir.system_pay.models import SystemPayTransaction, SystemPaySubscription

logger = logging.getLogger(__name__)


def update_payment_from_transaction(payment, transaction):
    if transaction.status == SystemPayTransaction.STATUS_COMPLETED:
        if payment.status == Payment.STATUS_CANCELED:
            logger.error(
                f"La transaction Systempay {transaction.pk} a été mise à jour alors que le paiement {payment.pk} était annulé"
            )
            return

        if transaction.is_refund:
            refund_payment(payment)
        else:
            complete_payment(payment)

    if (
        transaction.status == SystemPayTransaction.STATUS_REFUSED
        and payment.status == Payment.STATUS_WAITING
    ):
        refuse_payment(payment)


def update_subscription_from_transaction(subscription, sp_subscription, sp_transaction):
    # annulation des subscription côté systempay qui pourrait déjà exister pour cette souscription (notamment dans le
    # cas d'une souscription déjà existante avec simple changement d'alias et donc de souscription systempay)
    for old_sp_subscription in SystemPaySubscription.objects.filter(
        subscription=subscription, active=True
    ).exclude(pk=sp_subscription.pk):
        alias = old_sp_subscription.alias
        PAYMENT_MODES[subscription.mode].soap_client.cancel_alias(alias)
        alias.active = False
        alias.save(update_fields=["active"])
        old_sp_subscription.active = False
        old_sp_subscription.save(update_fields=["active"])

    if sp_transaction.status == SystemPayTransaction.STATUS_COMPLETED:
        if subscription.status in (
            Subscription.STATUS_CANCELED,
            Subscription.STATUS_TERMINATED,
        ):
            logger.error(
                f"La transaction Systempay {sp_transaction.pk} a été mise à jour alors que l'abonnement {subscription.pk} était annulé"
            )
            return

        complete_subscription(subscription)
