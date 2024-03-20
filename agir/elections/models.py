from datetime import datetime

import pytz as pytz
from django.core.exceptions import ValidationError
from django.db import models
from django_countries.fields import CountryField

from agir.lib.model_fields import ChoiceArrayField
from agir.lib.models import BaseAPIResource, SimpleLocationMixin

__all__ = ["PollingStationOfficer"]


class PollingStationOfficerQuerySet(models.QuerySet):
    def active(self):
        return self.exclude(person__isnull=True).exclude(person__role__is_active=False)


class PollingStationOfficer(BaseAPIResource, SimpleLocationMixin):
    GENDER_FEMALE = "F"
    GENDER_MALE = "M"
    GENDER_CHOICES = (
        (GENDER_FEMALE, "Femme"),
        (GENDER_MALE, "Homme"),
    )

    ROLE_ASSESSEURE_TITULAIRE = "AT"
    ROLE_ASSESSEURE_SUPPLEANTE = "AS"
    ROLE_DELEGUEE = "D"
    ROLE_CHOICES = (
        (ROLE_ASSESSEURE_TITULAIRE, "Assesseur·e titulaire"),
        (ROLE_ASSESSEURE_SUPPLEANTE, "Assesseur·e suppléant·e"),
        (ROLE_DELEGUEE, "Délégué·e"),
    )

    VOTING_DATE_CHOICES = (
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
            "9 juin 2024 — Élections européennes 2024",
        ),
    )

    objects = PollingStationOfficerQuerySet.as_manager()

    person = models.OneToOneField(
        "people.Person",
        verbose_name="personne",
        related_name="polling_station_officer",
        related_query_name="polling_station_officer",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    first_name = models.CharField(
        "prénoms",
        help_text="Tous les prénoms, tels qu'indiqués à l'état civil",
        max_length=255,
        null=False,
        blank=False,
    )
    last_name = models.CharField(
        "nom de famille",
        help_text="Le nom de famille, tel qu'indiqué à l'état civil",
        max_length=255,
        null=False,
        blank=False,
    )
    birth_name = models.CharField(
        "nom de naissance",
        help_text="Le nom de naissance, si différent du nom de famille",
        max_length=255,
        null=False,
        blank=True,
    )

    gender = models.CharField(
        "genre",
        help_text="Le genre tel qu'indiqué à l'état civil",
        max_length=1,
        null=False,
        blank=False,
        choices=GENDER_CHOICES,
    )

    birth_date = models.DateField("date de naissance", null=False, blank=False)
    birth_city = models.CharField(
        "ville de naissance",
        max_length=255,
        null=False,
        blank=False,
    )
    birth_country = CountryField(
        "pays de naissance",
        blank_label="(sélectionner un pays)",
        default="FR",
        null=False,
        blank=False,
    )

    voting_commune = models.ForeignKey(
        "data_france.Commune",
        verbose_name="commune",
        help_text="Commune d'inscription aux liste électorales",
        related_name="polling_station_officers",
        related_query_name="polling_station_officer",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    voting_consulate = models.ForeignKey(
        "data_france.CirconscriptionConsulaire",
        verbose_name="circonscription consulaire",
        help_text="Circonscription consulaire d'inscription aux liste électorales",
        related_name="polling_station_officers",
        related_query_name="polling_station_officer",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    voting_circonscription_legislative = models.ForeignKey(
        "data_france.CirconscriptionLegislative",
        verbose_name="circonscription législative",
        help_text="Circonscription législative d'inscription aux liste électorales",
        related_name="polling_station_officers",
        related_query_name="polling_station_officer",
        blank=False,
        null=True,
        on_delete=models.SET_NULL,
    )
    polling_station = models.CharField(
        "bureau de vote",
        max_length=255,
        null=False,
        blank=False,
    )
    voter_id = models.CharField(
        "numéro national d'électeur",
        max_length=255,
        blank=False,
        null=False,
    )

    role = models.CharField(
        "rôle",
        max_length=2,
        null=False,
        blank=False,
        choices=ROLE_CHOICES,
    )
    has_mobility = models.BooleanField(
        "Peut se déplacer",
        help_text="Peut ou non se déplacer dans un bureau de vote différent du sien",
        null=False,
        blank=False,
        default=False,
    )

    available_voting_dates = ChoiceArrayField(
        models.CharField(
            "date du scrutin",
            null=False,
            blank=False,
            max_length=255,
            choices=((str(date), label) for date, label in VOTING_DATE_CHOICES),
        ),
        verbose_name="dates de disponibilité",
        null=False,
        blank=False,
        default=list,
    )

    contact_email = models.EmailField(
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

    remarks = models.TextField("remarques", blank=True, null=False, default="")

    class Meta:
        verbose_name = "assesseur·e / délégué·e de bureau de vote"
        verbose_name_plural = "assesseur·es / délégué·es de bureau de vote"
        ordering = ("-modified",)
        indexes = (
            models.Index(
                fields=("modified",),
            ),
            models.Index(
                fields=("id", "modified"),
            ),
            models.Index(fields=("voting_commune",)),
            models.Index(fields=("voting_consulate",)),
        )
        constraints = (
            models.UniqueConstraint(
                fields=["contact_email"],
                name="polling_station_officer_unique_for_email",
            ),
        )

    def __str__(self):
        return f"{self.first_name} {self.last_name} <{self.contact_email}>"

    def clean(self):
        super().clean()
        if self.voting_commune_id is None and self.voting_consulate_id is None:
            raise ValidationError(
                "Au moins une commune ou une circonscription consulaire doit être sélectionnée"
            )
        if self.voting_commune_id is not None and self.voting_consulate_id is not None:
            raise ValidationError(
                "Une commune et une circonscription consulaire ne peuvent pas être sélectionnées en même temps"
            )
