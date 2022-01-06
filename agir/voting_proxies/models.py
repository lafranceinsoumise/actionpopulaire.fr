from datetime import datetime

import pytz
from data_france.models import Commune
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.functional import cached_property

from agir.lib.model_fields import ChoiceArrayField
from agir.lib.models import BaseAPIResource

__all__ = ["VotingProxy", "VotingProxyRequest"]


class AbstractVoter(BaseAPIResource):
    VOTING_DATE_CHOICES = (
        (
            datetime(2022, 4, 10, 0, 0, 0, tzinfo=pytz.timezone("Europe/Paris")).date(),
            "premier tour de l'élection présidentielle, dimanche 10 avril 2022",
        ),
        (
            datetime(2022, 4, 24, 0, 0, 0, tzinfo=pytz.timezone("Europe/Paris")).date(),
            "second tour de l'élection présidentielle, dimanche 24 avril 2022",
        ),
        (
            datetime(2022, 6, 12, 0, 0, 0, tzinfo=pytz.timezone("Europe/Paris")).date(),
            "premier tour des élections législatives, dimanche 12 juin 2022",
        ),
        (
            datetime(2022, 6, 19, 0, 0, 0, tzinfo=pytz.timezone("Europe/Paris")).date(),
            "second tour des élections législatives, dimanche 19 juin 2022",
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
        "numéro du bureau de vote",
        max_length=255,
        null=False,
        blank=False,
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


class VotingProxyRequest(AbstractVoter):
    STATUS_CREATED = "created"
    STATUS_ACCEPTED = "accepted"
    STATUS_CONFIRMED = "confirmed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = (
        (STATUS_CREATED, "demande créée"),
        (STATUS_ACCEPTED, "demande acceptée"),
        (STATUS_CONFIRMED, "procuration confirmée"),
        (STATUS_CANCELLED, "demande annulée"),
    )

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

    def get_voting_proxy_information(self):
        if self.proxy is None:
            return ""
        voting_dates = self.proxy.voting_proxy_requests.filter(
            email=self.email
        ).values_list("voting_date", flat=True)
        voting_date_string = ", ".join(
            [voting_date.strftime("%d/%m/%Y") for voting_date in voting_dates]
        )
        text = (
            f"Procuration de vote ({voting_date_string}) : "
            f"{self.proxy.first_name} {self.proxy.last_name.upper()} "
            f"- né·e le {self.proxy.date_of_birth.strftime('%d/%m/%Y')}"
            f"- tél. {self.proxy.contact_phone} "
        )
        if self.proxy.remarks:
            text += f"- {self.proxy.remarks}"
        text += "."
        return text
