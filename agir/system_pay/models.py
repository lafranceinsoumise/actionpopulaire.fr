from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_prometheus.models import ExportModelOperationsMixin

from agir.lib.models import TimeStampedModel


class SystemPayTransaction(
    ExportModelOperationsMixin("system_pay_transaction"), TimeStampedModel
):
    STATUS_WAITING = 0
    STATUS_COMPLETED = 1
    STATUS_ABANDONED = 2
    STATUS_CANCELED = 3
    STATUS_REFUSED = 4

    STATUS_CHOICES = (
        (STATUS_WAITING, "En attente"),
        (STATUS_COMPLETED, "Terminé"),
        (STATUS_ABANDONED, "Abandonné"),
        (STATUS_CANCELED, "Annulé"),
        (STATUS_REFUSED, "Refusé"),
    )

    status = models.IntegerField(
        "status", choices=STATUS_CHOICES, default=STATUS_WAITING
    )
    payment = models.ForeignKey("payments.Payment", on_delete=models.PROTECT)
    webhook_calls = JSONField(_("Événements de paiement"), blank=True, default=list)
