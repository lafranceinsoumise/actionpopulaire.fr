from django.contrib import messages
from django.db import transaction

from agir.checks.models import CheckPayment
from agir.payments.actions.payments import (
    notify_status_change,
    change_payment_status,
    PaymentException,
    log_payment_event,
)
from agir.payments.payment_modes import PAYMENT_MODES


def notify_status_action(model_admin, request, queryset):
    for p in queryset:
        notify_status_change(p)


notify_status_action.short_description = "Renotifier le statut"


def change_payments_status_action(status, description):
    def action(modeladmin, request, queryset):
        try:
            with transaction.atomic():
                for payment in queryset.filter(status=CheckPayment.STATUS_WAITING):
                    if not PAYMENT_MODES[payment.mode].can_admin:
                        raise PaymentException(
                            "Paiement n°{} ne peut pas être changé manuellement".format(
                                payment.id
                            )
                        )

                    log_payment_event(
                        payment,
                        event="status_change",
                        old_status=payment.status,
                        new_status=status,
                        origin="payment_admin_action",
                        user=request.user,
                    )
                    change_payment_status(payment, status)
        except PaymentException as exception:
            modeladmin.message_user(request, exception, level=messages.WARNING)

    # have to change the function name so that django admin see that they are different functions
    action.__name__ = f"change_to_{status}"
    action.short_description = description

    return action
