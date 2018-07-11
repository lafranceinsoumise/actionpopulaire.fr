import logging

from agir.payments.actions import complete_payment
from agir.payments.models import Payment
from agir.system_pay.models import SystemPayTransaction

logger = logging.getLogger(__name__)

def update_payment_from_transaction(payment, transaction):
    if transaction.status == SystemPayTransaction.STATUS_COMPLETED:
        if payment.status == Payment.STATUS_CANCELED:
            logger.error(f"La transaction Systempay {transaction.pk} a été mise à jour alors que le paiement {payment.pk} était annulé")
            return

        complete_payment(payment)
