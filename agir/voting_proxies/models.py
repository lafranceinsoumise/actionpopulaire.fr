from datetime import datetime, timedelta

import pytz
from data_france.models import Commune
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Exists, OuterRef
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.html import escape
from django.utils.safestring import mark_safe

from agir.elections.utils import (
    get_polling_station_label,
    get_polling_station_circonscription,
)
from agir.groups.models import Membership
from agir.lib.model_fields import ChoiceArrayField
from agir.lib.models import BaseAPIResource

__all__ = ["VotingProxy", "VotingProxyRequest"]

from agir.lib.sms.common import to_7bit_string
from agir.lib.utils import front_url
from agir.payments.models import Payment


class AbstractVoter(BaseAPIResource):
    VOTING_DATE_CHOICES = (
        (
            datetime(2022, 4, 10, 0, 0, 0, tzinfo=pytz.timezone("Europe/Paris")).date(),
            "10 avril 2022 — 1er tour de la présidentielle",
        ),
        (
            datetime(2022, 4, 24, 0, 0, 0, tzinfo=pytz.timezone("Europe/Paris")).date(),
            "24 avril 2022 — 2nd tour de la présidentielle",
        ),
        (
            datetime(2022, 6, 12, 0, 0, 0, tzinfo=pytz.timezone("Europe/Paris")).date(),
            "12 juin 2022 — 1er tour des législatives",
        ),
        (
            datetime(2022, 6, 19, 0, 0, 0, tzinfo=pytz.timezone("Europe/Paris")).date(),
            "19 juin 2022 — 2nd tour des législatives",
        ),
        (
            datetime(2024, 6, 9, 0, 0, 0, tzinfo=pytz.timezone("Europe/Paris")).date(),
            "Dimanche 9 juin 2024 (samedi 8 juin pour la Guadeloupe, la Martinique, "
            "la Guyane, la Polynésie française et les Français·es de l'étranger résidant sur le continent américain) — "
            "Élections européennes 2024",
        ),
        (
            datetime(2024, 6, 30, 0, 0, 0, tzinfo=pytz.timezone("Europe/Paris")).date(),
            "Dimanche 30 juin 2024 (samedi 29 juin pour la Guadeloupe, la Martinique, la Guyane, la Polynésie française "
            "et les Français·es de l'étranger résidant sur le continent américain) — 1er tour des législatives",
        ),
        (
            datetime(2024, 7, 7, 0, 0, 0, tzinfo=pytz.timezone("Europe/Paris")).date(),
            "Dimanche 7 juillet 2024 (samedi 6 juillet pour la Guadeloupe, la Martinique, la Guyane, la Polynésie "
            "française et les Français·es de l'étranger résidant sur le continent américain) — 2nd tour des "
            "législatives",
        ),
    )

    first_name = models.CharField(
        "prénoms",
        help_text="Les prénoms tels qu'ils apparaissent sur la carte électorale",
        max_length=255,
        null=False,
        blank=False,
    )
    last_name = models.CharField(
        "nom de famille",
        help_text="Le nom de famille tel qu'il apparaît sur la carte électorale",
        max_length=255,
        null=False,
        blank=False,
    )
    email = models.EmailField(
        "adresse email",
        null=False,
        blank=False,
    )
    contact_phone = models.CharField(
        "numéro de téléphone",
        max_length=30,
        null=False,
        blank=False,
    )
    commune = models.ForeignKey(
        "data_france.Commune",
        verbose_name="Commune",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    consulate = models.ForeignKey(
        "data_france.CirconscriptionConsulaire",
        verbose_name="Circonscription consulaire",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    polling_station_number = models.CharField(
        "bureau de vote",
        max_length=255,
        null=False,
        blank=True,
    )
    voter_id = models.CharField(
        "numéro national d'électeur", max_length=255, blank=True, null=False, default=""
    )

    @property
    def polling_station_label(self):
        if not self.polling_station_number:
            return ""

        return get_polling_station_label(
            self.polling_station_number,
            fallback=self.polling_station_number,
        )

    @property
    def circonscription_legislative(self):
        if self.consulate:
            return self.consulate.circonscription_legislative.code

        if not self.polling_station_number:
            return ""

        return get_polling_station_circonscription(
            self.polling_station_number,
            fallback="",
        )

    def clean(self):
        super().clean()
        if self.commune is None and self.consulate is None:
            raise ValidationError(
                "Au moins une commune ou une circonscription consulaire doit être sélectionnée"
            )
        if self.commune is not None and self.consulate is not None:
            raise ValidationError(
                "Une commune et une circonscription consulaire ne peuvent pas être sélectionnées en même temps"
            )

    class Meta:
        abstract = True
        ordering = ("-updated",)
        indexes = (
            models.Index(
                fields=("updated",),
            ),
            models.Index(
                fields=("id", "updated"),
            ),
            models.Index(fields=("commune",)),
            models.Index(fields=("consulate",)),
        )


class VotingProxyQuerySet(models.QuerySet):
    def active(self):
        return self.exclude(person__isnull=True).exclude(
            person__role__isnull=False, person__role__is_active=False
        )

    def available(self):
        return self.active().filter(
            status__in=(VotingProxy.STATUS_CREATED, VotingProxy.STATUS_AVAILABLE),
        )

    def reliable(self):
        # Allows only people that existed before the campaign start or have donated or have joined a group
        return (
            self.available()
            .annotate(
                has_donation=Exists(
                    Payment.objects.completed().filter(person=OuterRef("person"))
                ),
                has_group=Exists(
                    Membership.objects.active()
                    .active_members()
                    .filter(person=OuterRef("person"))
                ),
            )
            .exclude(
                person__created__gte="2024-06-09T20:00:00+0200",
                has_donation=False,
                has_group=False,
                voting_proxy_requests__isnull=True,
            )
        )


class VotingProxy(AbstractVoter):
    STATUS_CREATED = "created"
    STATUS_INVITED = "invited"
    STATUS_AVAILABLE = "available"
    STATUS_UNAVAILABLE = "unavailable"
    STATUS_CHOICES = (
        (STATUS_CREATED, "créé"),
        (STATUS_INVITED, "invité"),
        (STATUS_AVAILABLE, "disponible"),
        (STATUS_UNAVAILABLE, "indisponible"),
    )

    objects = VotingProxyQuerySet.as_manager()

    date_of_birth = models.DateField("Date de naissance", null=True, blank=False)
    person = models.OneToOneField(
        "people.Person",
        verbose_name="Personne",
        on_delete=models.SET_NULL,
        related_name="voting_proxy",
        null=True,
        blank=True,
    )
    status = models.CharField(
        "statut",
        max_length=255,
        null=False,
        blank=False,
        choices=STATUS_CHOICES,
        default=STATUS_CREATED,
    )
    voting_dates = ChoiceArrayField(
        models.CharField(
            "date du scrutin",
            null=False,
            blank=False,
            max_length=255,
            choices=(
                (str(date), label) for date, label in AbstractVoter.VOTING_DATE_CHOICES
            ),
        ),
        verbose_name="dates de disponibilité",
        null=False,
        blank=False,
        default=list,
    )
    remarks = models.TextField("remarques", blank=True, null=False, default="")
    last_matched = models.DateTimeField(
        "date de la dernière proposition de procuration",
        null=True,
        blank=False,
        editable=False,
    )

    class Meta:
        verbose_name = "volontaire pour le vote par procuration"
        verbose_name_plural = "volontaires pour le vote par procuration"
        constraints = (
            models.UniqueConstraint(
                fields=["email"],
                name="unique_for_email",
            ),
        )

    def __str__(self):
        return f"{self.first_name} {self.last_name} <{self.email}>"

    @cached_property
    def available_voting_dates(self):
        accepted_dates = [
            str(date)
            for date in self.voting_proxy_requests.values_list("voting_date", flat=True)
        ]
        return [date for date in self.voting_dates if date not in accepted_dates]

    def is_active(self):
        if self.person is None:
            return False

        if self.person.role and not self.person.role.is_active:
            return False

        return True

    def is_available(self):
        return (
            self.is_active()
            and self.status
            in (
                self.STATUS_CREATED,
                self.STATUS_AVAILABLE,
            )
            and len(self.available_voting_dates) > 0
        )


class VotingProxyRequestQuerySet(models.QuerySet):
    def upcoming(self):
        return self.filter(
            voting_date__gte=timezone.now().date(),
        )

    def pending(self):
        return self.upcoming().filter(
            status=VotingProxyRequest.STATUS_CREATED,
            proxy__isnull=True,
        )

    def waiting_confirmation(self):
        return self.upcoming().filter(
            status=VotingProxyRequest.STATUS_ACCEPTED,
            proxy__isnull=False,
        )


class VotingProxyRequest(AbstractVoter):
    STATUS_CREATED = "created"
    STATUS_ACCEPTED = "accepted"
    STATUS_CONFIRMED = "confirmed"
    STATUS_CANCELLED = "cancelled"
    STATUS_FORWARDED = "forwarded"

    STATUS_CHOICES = (
        (STATUS_CREATED, "demande créée"),
        (STATUS_ACCEPTED, "demande acceptée"),
        (STATUS_CONFIRMED, "procuration confirmée"),
        (STATUS_CANCELLED, "demande annulée"),
        (STATUS_FORWARDED, "demande transférée à l'équipe de campagne"),
    )

    objects = VotingProxyRequestQuerySet.as_manager()

    status = models.CharField(
        "statut de la demande",
        max_length=255,
        null=False,
        blank=False,
        choices=STATUS_CHOICES,
        default=STATUS_CREATED,
    )
    voting_date = models.DateField(
        "date du scrutin",
        null=False,
        blank=False,
        choices=AbstractVoter.VOTING_DATE_CHOICES,
    )
    proxy = models.ForeignKey(
        "voting_proxies.VotingProxy",
        verbose_name="Volontaire",
        on_delete=models.SET_NULL,
        related_name="voting_proxy_requests",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "demande de vote par procuration"
        verbose_name_plural = "demandes de vote par procuration"
        constraints = (
            models.UniqueConstraint(
                fields=["email", "voting_date"],
                name="unique_for_email_and_voting_date",
            ),
            models.UniqueConstraint(
                fields=["proxy", "voting_date"],
                name="unique_for_proxy_and_voting_date",
                condition=models.Q(proxy__isnull=False),
            ),
        )

    def __str__(self):
        return (
            f"{self.first_name} {self.last_name} <{self.email}> --> {self.voting_date}"
        )

    @property
    def reply_to_url(self):
        return front_url("reply_to_single_voting_proxy_request", args=(self.pk,))

    def is_upcoming(self):
        return self.voting_date >= (timezone.now() + timedelta(days=2)).date()

    def is_pending(self):
        return (
            self.is_upcoming()
            and self.status == self.STATUS_CREATED
            and self.proxy is None
        )

    def _get_voting_proxy_information_as_html(self):
        voting_dates = self.proxy.voting_proxy_requests.filter(
            email=self.email
        ).values_list("voting_date", flat=True)
        voting_date_string = ", ".join(
            [voting_date.strftime("%d/%m/%Y") for voting_date in voting_dates]
        )
        text = (
            f"Date(s)&nbsp;: <strong>{escape(voting_date_string)}</strong><br>"
            f"Volontaire&nbsp;: <strong>{escape(self.proxy.first_name)} {escape(self.proxy.last_name.upper())}</strong><br>"
            f"Né·e le: <strong>{escape(self.proxy.date_of_birth.strftime('%d/%m/%Y'))}</strong><br>"
            f"Téléphone&nbsp;: <strong>{escape(self.proxy.contact_phone)}</strong>"
        )

        if self.proxy.commune:
            text += (
                f"<br>Commune&nbsp;: <strong>{self.proxy.commune.nom_complet}</strong>"
            )
        else:
            text += f"<br>Consulat&nbsp;: <strong>{self.proxy.consulate.nom}</strong>"

        if self.proxy.polling_station_number:
            text += f"<br>Bureau de vote&nbsp;: <strong>{escape(self.proxy.polling_station_label)}</strong>"

        if self.proxy.voter_id:
            text += f"<br>Numéro national d'électeur&nbsp;: <strong>{escape(self.proxy.voter_id)}</strong>"

        if self.proxy.remarks:
            text += f"<br>Disponibilités&nbsp;: <strong>{escape(self.proxy.remarks)}</strong>"

        return mark_safe(text)

    def _get_voting_proxy_information_as_text(self):
        voting_dates = self.proxy.voting_proxy_requests.filter(
            email=self.email
        ).values_list("voting_date", flat=True)
        voting_date_string = ", ".join(
            [voting_date.strftime("%d/%m/%Y") for voting_date in voting_dates]
        )
        text = (
            f"Procuration de vote ({voting_date_string}) :"
            f" {to_7bit_string(self.proxy.first_name)} {to_7bit_string(self.proxy.last_name.upper())}"
            f" - né·e le {self.proxy.date_of_birth.strftime('%d/%m/%Y')}"
            f" - tél. {self.proxy.contact_phone}"
        )

        if self.proxy.commune:
            text += f" - commune: {to_7bit_string(self.proxy.commune.nom_complet)}"
        else:
            text += f" - consulat: {to_7bit_string(self.proxy.consulate.nom)}"

        if self.proxy.polling_station_number:
            text += f" - bureau: {to_7bit_string(self.proxy.polling_station_label)}"

        if self.proxy.voter_id:
            text += f" - NNE: {to_7bit_string(self.proxy.voter_id)}"

        if self.proxy.remarks:
            text += f" - {to_7bit_string(self.proxy.remarks)}"

        return text

    def get_voting_proxy_information(self, as_html=False):
        if self.proxy is None:
            return ""

        if as_html:
            return self._get_voting_proxy_information_as_html()

        return self._get_voting_proxy_information_as_text()
