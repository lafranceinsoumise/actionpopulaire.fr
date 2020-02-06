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
    payment = models.ForeignKey(
        "payments.Payment", on_delete=models.PROTECT, null=True, editable=False
    )
    is_refund = models.BooleanField("Remboursement", default=False)

    # Ce champ est utilisé pour la transaction SystemPay qui initie la souscription
    # En effet, cette transaction n'est PAS associée à un Payment (mais à la souscription)
    # Par la suite, les transactions liées aux paiement de la souscription ne
    # renseignent PAS ce champ (mais le Payment correspondant le fait !)
    subscription = models.ForeignKey(
        "payments.Subscription", on_delete=models.PROTECT, null=True, editable=False
    )
    webhook_calls = JSONField(_("Événements de paiement"), blank=True, default=list)
    alias = models.ForeignKey("SystemPayAlias", on_delete=models.SET_NULL, null=True)
    uuid = models.UUIDField(
        "UUID fourni par SystemPay", unique=True, blank=True, null=True
    )


class SystemPayAlias(ExportModelOperationsMixin("system_pay_alias"), TimeStampedModel):
    identifier = models.UUIDField("Alias de la carte bancaire", unique=True)
    active = models.BooleanField("L'alias est actif côté systempay", default=True)
    expiry_date = models.DateField("Date d'expiration de la carte bancaire")


class SystemPaySubscription(
    ExportModelOperationsMixin("system_pay_subscription"), TimeStampedModel
):
    identifier = models.CharField(
        "Identifiant de la souscription", unique=True, max_length=30, blank=False
    )
    alias = models.ForeignKey("SystemPayAlias", null=False, on_delete=models.PROTECT)
    subscription = models.ForeignKey(
        "payments.Subscription",
        null=False,
        on_delete=models.PROTECT,
        related_name="system_pay_subscriptions",
    )

    active = models.BooleanField(
        "La souscription est active côté SystemPay", default=True
    )
