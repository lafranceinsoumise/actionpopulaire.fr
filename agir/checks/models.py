from django.utils.translation import gettext_lazy as _

from agir.checks import AbstractCheckPaymentMode
from agir.payments.models import Payment, PaymentManager

__all__ = ["CheckPayment"]


class CheckPaymentManager(PaymentManager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                mode__in=[
                    klass.id for klass in AbstractCheckPaymentMode.__subclasses__()
                ]
            )
        )


class CheckPayment(Payment):
    objects = CheckPaymentManager()

    class Meta:
        verbose_name = _("Paiement par chèque")
        verbose_name_plural = _("Paiements par chèque")
        proxy = True
