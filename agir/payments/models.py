from django.contrib.postgres.fields import JSONField
from django.db import models
from django.template.defaultfilters import floatformat
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django_prometheus.models import ExportModelOperationsMixin
from phonenumber_field.modelfields import PhoneNumberField

from agir.lib.models import LocationMixin, TimeStampedModel
from agir.lib.display import display_address
from .types import get_payment_choices
from .payment_modes import PAYMENT_MODES


class PaymentQueryset(models.QuerySet):
    def awaiting(self):
        return self.filter(status=Payment.STATUS_WAITING)

    def completed(self):
        return self.filter(status=Payment.STATUS_COMPLETED)

    def failed(self):
        return self.filter(
            status__in=[
                Payment.STATUS_ABANDONED,
                Payment.STATUS_CANCELED,
                Payment.STATUS_REFUSED,
            ]
        )


PaymentManager = models.Manager.from_queryset(
    PaymentQueryset, class_name="PaymentManager"
)


class Payment(ExportModelOperationsMixin("payment"), TimeStampedModel, LocationMixin):
    objects = PaymentManager()

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

    person = models.ForeignKey(
        "people.Person", on_delete=models.SET_NULL, null=True, related_name="payments"
    )

    email = models.EmailField("email", max_length=255)
    first_name = models.CharField("prénom", max_length=255)
    last_name = models.CharField("nom de famille", max_length=255)
    phone_number = PhoneNumberField("numéro de téléphone", null=True)

    type = models.CharField("type", choices=get_payment_choices(), max_length=255)
    mode = models.CharField(
        _("Mode de paiement"), max_length=70, null=False, blank=False
    )

    price = models.IntegerField(_("prix en centimes d'euros"))
    status = models.IntegerField(
        "status", choices=STATUS_CHOICES, default=STATUS_WAITING
    )
    meta = JSONField(blank=True, default=dict)
    events = JSONField(_("Événements de paiement"), blank=True, default=list)
    subscription = models.ForeignKey(
        "Subscription",
        on_delete=models.PROTECT,
        related_name="payments",
        null=True,
        blank=True,
    )

    def get_price_display(self):
        return "{} €".format(floatformat(self.price / 100, 2))

    def get_mode_display(self):
        return (
            PAYMENT_MODES[self.mode].label if self.mode in PAYMENT_MODES else self.mode
        )

    def get_payment_url(self):
        return reverse("payment_page", args=[self.pk])

    def can_retry(self):
        return (
            self.mode in PAYMENT_MODES
            and PAYMENT_MODES[self.mode].can_retry
            and self.status != self.STATUS_COMPLETED
        )

    def can_cancel(self):
        return (
            self.mode in PAYMENT_MODES
            and PAYMENT_MODES[self.mode].can_cancel
            and self.status != self.STATUS_COMPLETED
        )

    def html_full_address(self):
        return display_address(self)

    def description(self):
        from agir.payments.actions.payments import description_for_payment

        return description_for_payment(self)

    def __str__(self):
        return _("Paiement n°") + str(self.id)

    def __repr__(self):
        return "{klass}(id={id!r}, email={email!r}, status={status!r}, type={type!r}, mode={mode!r}, price={price!r})".format(
            klass=self.__class__.__name__,
            id=self.id,
            email=self.email,
            status=self.status,
            type=self.type,
            mode=self.mode,
            price=self.price,
        )

    class Meta:
        get_latest_by = "created"


class Subscription(ExportModelOperationsMixin("subscription"), TimeStampedModel):
    STATUS_WAITING = 0
    STATUS_COMPLETED = 1
    STATUS_ABANDONED = 2
    STATUS_CANCELED = 3
    STATUS_REFUSED = 4
    STATUS_TERMINATED = 5

    STATUS_CHOICES = (
        (STATUS_WAITING, "Souscription en attente"),
        (STATUS_COMPLETED, "Souscription active"),
        (STATUS_ABANDONED, "Souscription abandonnée"),
        (STATUS_CANCELED, "Souscription annulée"),
        (STATUS_REFUSED, "Souscription refusée"),
        (STATUS_TERMINATED, "Souscription désactivée"),
    )

    person = models.ForeignKey(
        "people.Person",
        on_delete=models.SET_NULL,
        null=True,
        related_name="subscriptions",
    )

    day_of_month = models.PositiveSmallIntegerField(
        "Jour du mois", blank=True, null=True, editable=False
    )

    price = models.IntegerField("prix en centimes d'euros", editable=False)
    type = models.CharField("Type", max_length=255)
    mode = models.CharField(
        _("Mode de paiement"), max_length=70, null=False, blank=False
    )
    status = models.IntegerField(
        "status", choices=STATUS_CHOICES, default=STATUS_WAITING
    )
    meta = JSONField(blank=True, default=dict)

    end_date = models.DateField("Fin de l'abonnement", blank=True, null=True)

    def get_price_display(self):
        return "{} €".format(floatformat(self.price / 100, 2))

    def get_mode_display(self):
        return (
            PAYMENT_MODES[self.mode].label if self.mode in PAYMENT_MODES else self.mode
        )

    def description(self):
        from agir.payments.actions.subscriptions import description_for_subscription

        return description_for_subscription(self)

    def __str__(self):
        return "Abonnement n°" + str(self.id)

    class Meta:
        verbose_name = "Paiement récurrent"
        verbose_name_plural = "Paiements récurrents"
