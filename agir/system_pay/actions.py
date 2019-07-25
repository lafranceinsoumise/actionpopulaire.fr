import logging

from agir.payments.actions.payments import complete_payment, refuse_payment
from agir.payments.actions.subscriptions import complete_subscription
from agir.payments.models import Payment, Subscription
from agir.system_pay.models import SystemPayTransaction, SystemPayAlias

logger = logging.getLogger(__name__)


def update_payment_from_transaction(payment, transaction):
    if transaction.status == SystemPayTransaction.STATUS_COMPLETED:
        if payment.status == Payment.STATUS_CANCELED:
            logger.error(
                f"La transaction Systempay {transaction.pk} a été mise à jour alors que le paiement {payment.pk} était annulé"
            )
            return

        complete_payment(payment)

    if (
        transaction.status == SystemPayTransaction.STATUS_REFUSED
        and payment.status == Payment.STATUS_WAITING
    ):
        refuse_payment(payment)


def update_subscription_from_transaction(subscription, transaction):
    if transaction.status == SystemPayTransaction.STATUS_COMPLETED:
        if subscription.status in (
            Subscription.STATUS_CANCELED,
            Subscription.STATUS_TERMINATED,
        ):
            logger.error(
                f"La transaction Systempay {transaction.pk} a été mise à jour alors que l'abonnement {subscription.pk} était annulé"
            )
            return

        complete_subscription(subscription)
