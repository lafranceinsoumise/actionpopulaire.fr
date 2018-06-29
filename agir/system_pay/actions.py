from agir.payments.models import Payment
from agir.system_pay.models import SystemPayTransaction


def update_payment_from_transactions(payment):
    transactions = SystemPayTransaction.objects.filter(payment=payment)
    if SystemPayTransaction.STATUS_COMPLETED in [t.status for t in transactions]:
        payment.status = Payment.STATUS_COMPLETED
        payment.save()
