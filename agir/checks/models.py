from django.utils.translation import ugettext_lazy as _

from agir.payments.models import Payment, PaymentManager

from . import CheckPaymentMode


class CheckPaymentManager(PaymentManager):
    def get_queryset(self):
        return super().get_queryset().filter(mode=CheckPaymentMode.id)


class CheckPayment(Payment):
    objects = CheckPaymentManager()

    class Meta:
        verbose_name = _("Paiement par chèque")
        verbose_name_plural = _("Paiements par chèque")
        proxy = True
