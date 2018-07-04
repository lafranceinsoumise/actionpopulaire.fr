import logging

from agir.payments.actions import complete_payment
from agir.payments.models import Payment
from agir.system_pay.models import SystemPayTransaction

logger = logging.getLogger(__name__)

def update_payment_from_transactions(payment):
    transactions = SystemPayTransaction.objects.filter(payment=payment)
    if payment.status == Payment.STATUS_CANCELED:
        logger.error("Une transaction Systempay a été validée alors que le paiement était annulé")
        return
    if SystemPayTransaction.STATUS_COMPLETED in [t.status for t in transactions]:
        complete_payment(payment)
