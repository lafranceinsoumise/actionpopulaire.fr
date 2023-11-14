import calendar
import json
import math

from agir.lib.form_fields import CustomJSONEncoder
from django.db import models
from django.db.models import JSONField, TextChoices, Q
from django.template.defaultfilters import floatformat
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_prometheus.models import ExportModelOperationsMixin
from num2words import num2words
from phonenumber_field.modelfields import PhoneNumberField

from agir.lib.display import display_address, display_price, display_allocations
from agir.lib.models import LocationMixin, TimeStampedModel
from agir.lib.utils import front_url
from agir.payments.model_fields import AmountField
from .payment_modes import PAYMENT_MODES
from .types import PAYMENT_TYPES

__all__ = ["Payment", "Subscription"]

from ..checks import AbstractCheckPaymentMode


class FrequenceDon(TextChoices):
    MENSUEL = "M", "par mois"
    ANNUEL = "A", "par an"


def display_date_prelevement(day_of_month, month_of_year=None):
    if month_of_year is None:
        return f"{day_of_month} du mois"
    return f"{day_of_month} {calendar.month_name[month_of_year]}"


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

    def checks(self):
        check_modes = [
            key
            for key, payment_mode in PAYMENT_MODES.items()
            if isinstance(payment_mode, AbstractCheckPaymentMode)
        ]
        return self.filter(mode__in=check_modes)

    def contributions(self):
        from agir.donations.apps import DonsConfig

        return self.filter(type=DonsConfig.CONTRIBUTION_TYPE)

    def active_contribution(self):
        return (
            self.contributions()
            .completed()
            .exclude(meta__end_date__isnull=True)
            .filter(meta__end_date__gte=timezone.now().isoformat())
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
    STATUS_REFUND = -1

    STATUS_CHOICES = (
        (STATUS_WAITING, "Paiement en attente"),
        (STATUS_COMPLETED, "Paiement terminé"),
        (STATUS_ABANDONED, "Paiement abandonné en cours"),
        (STATUS_CANCELED, "Paiement annulé avant encaissement"),
        (STATUS_REFUSED, "Paiement refusé par votre banque"),
        (STATUS_REFUND, "Paiement remboursé"),
    )

    person = models.ForeignKey(
        "people.Person", on_delete=models.SET_NULL, null=True, related_name="payments"
    )

    email = models.EmailField("email", max_length=255)
    first_name = models.CharField("prénom", max_length=255)
    last_name = models.CharField("nom de famille", max_length=255)
    phone_number = PhoneNumberField("numéro de téléphone", null=True)

    type = models.CharField("type", max_length=255)
    mode = models.CharField(
        _("Mode de paiement"), max_length=70, null=False, blank=False
    )

    price = AmountField(_("Prix"))
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
        if not isinstance(self.price, int):
            return "-"
        return "{} €".format(floatformat(self.price / 100, 2))

    get_price_display.short_description = "Prix"

    def get_price_as_text(self):
        cents, euros = math.modf(self.price / 100)
        cents = math.floor(cents * 100)
        text = num2words(int(euros), lang="fr") + " euros"
        text = text.capitalize()
        if cents <= 0:
            return text
        return text + f" et {cents} centîmes"

    get_price_as_text.short_description = "Prix en toutes lettres"

    def get_mode_display(self):
        return (
            PAYMENT_MODES[self.mode].title if self.mode in PAYMENT_MODES else self.mode
        )

    get_mode_display.short_description = "Mode de paiement"

    def get_type_display(self):
        return (
            PAYMENT_TYPES[self.type].label if self.type in PAYMENT_TYPES else self.type
        )

    get_type_display.short_description = "Type de paiement"

    def get_allocations_display(self):
        allocations = self.meta.get("allocations", "[]")
        allocations = json.loads(allocations)
        return display_allocations(allocations)

    get_allocations_display.short_description = "Don fléché"

    def get_payment_url(self):
        return front_url("payment_page", args=[self.pk])

    def is_done(self):
        return self.status in (self.STATUS_COMPLETED, self.STATUS_REFUND)

    def is_cancelled(self):
        return self.status in (self.STATUS_CANCELED, self.STATUS_REFUND)

    def can_retry(self):
        return (
            self.mode in PAYMENT_MODES
            and PAYMENT_MODES[self.mode].can_retry
            and not self.is_done()
        )

    def can_cancel(self):
        return (
            self.mode in PAYMENT_MODES
            and PAYMENT_MODES[self.mode].can_cancel
            and self.status != self.STATUS_COMPLETED
        )

    def can_refund(self):
        return (
            self.mode in PAYMENT_MODES
            and PAYMENT_MODES[self.mode].can_refund
            and self.status == self.STATUS_COMPLETED
        )

    def is_check(self):
        return (
            self.mode in PAYMENT_MODES
            and isinstance(PAYMENT_MODES[self.mode], AbstractCheckPaymentMode),
        )

    def html_full_address(self):
        return display_address(self)

    @property
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
        ordering = ("-created",)
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"


class SubscriptionQueryset(models.QuerySet):
    def active(self):
        return self.filter(status=Subscription.STATUS_ACTIVE).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=timezone.now())
        )

    def contributions(self):
        from agir.donations.apps import DonsConfig

        return self.filter(type=DonsConfig.CONTRIBUTION_TYPE)

    def active_contributions(self):
        return (
            self.contributions()
            .filter(status=Subscription.STATUS_ACTIVE)
            .filter(end_date__gte=timezone.now())
        )


SubscriptionManager = models.Manager.from_queryset(
    SubscriptionQueryset, class_name="SubscriptionManager"
)


class Subscription(ExportModelOperationsMixin("subscription"), TimeStampedModel):
    objects = SubscriptionManager()

    STATUS_WAITING = 0
    STATUS_ACTIVE = 1
    STATUS_ABANDONED = 2
    STATUS_CANCELED = 3
    STATUS_REFUSED = 4
    STATUS_TERMINATED = 5

    STATUS_CHOICES = (
        (STATUS_WAITING, "Souscription en attente de confirmation par SystemPay"),
        (STATUS_ACTIVE, "Souscription active"),
        (STATUS_ABANDONED, "Souscription abandonnée avant complétion par la personne"),
        (STATUS_CANCELED, "Souscription refusée côté FI"),
        (STATUS_REFUSED, "Souscription refusée côté banque"),
        (STATUS_TERMINATED, "Souscription terminée"),
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
    month_of_year = models.PositiveSmallIntegerField(
        "Mois de l'année", blank=True, null=True, editable=False
    )

    price = models.IntegerField("prix en centimes d'euros", editable=False)
    type = models.CharField("Type", max_length=255)
    mode = models.CharField(
        _("Mode de paiement"), max_length=70, null=False, blank=False
    )
    status = models.IntegerField(
        "status", choices=STATUS_CHOICES, default=STATUS_WAITING
    )
    meta = JSONField(blank=True, default=dict, encoder=CustomJSONEncoder)

    effect_date = models.DateTimeField(
        _("Début de l'abonnement"), blank=True, null=True
    )
    end_date = models.DateField(_("Fin de l'abonnement"), blank=True, null=True)

    def get_price_display(self):
        return display_price(self.price)

    get_price_display.short_description = "Prix"

    def get_allocations_display(self):
        allocations = self.meta.get("allocations", "[]")
        allocations = json.loads(allocations)
        return display_allocations(allocations)

    get_allocations_display.short_description = "Don fléché"

    def get_mode_display(self):
        return (
            PAYMENT_MODES[self.mode].label if self.mode in PAYMENT_MODES else self.mode
        )

    get_mode_display.short_description = "Mode de paiement"

    def get_type_display(self):
        return (
            PAYMENT_TYPES[self.type].label if self.type in PAYMENT_TYPES else self.type
        )

    get_type_display.short_description = "Type d'abonnement"

    @property
    def description(self):
        from agir.payments.actions.subscriptions import description_for_subscription

        return description_for_subscription(self)

    @property
    def frequence(self):
        if self.month_of_year is None:
            return FrequenceDon.MENSUEL
        else:
            return FrequenceDon.ANNUEL

    def get_date_prelevement(self):
        return display_date_prelevement(self.day_of_month, self.month_of_year)

    def __str__(self):
        return "Abonnement n°" + str(self.id)

    class Meta:
        verbose_name = "Paiement récurrent"
        verbose_name_plural = "Paiements récurrents"
