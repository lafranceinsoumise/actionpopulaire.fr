import datetime

import reversion
from django.contrib.postgres.fields import ArrayField, DateRangeField
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from psycopg2._range import DateRange

from agir.lib.history import HistoryMixin

DELEGATIONS_CHOICES = (
    ("social", "Action sociale"),
    ("civiles juridiques", "Affaires civiles et juridiques"),
    ("économie", "Affaires économiques"),
    ("école", "Affaires scolaires"),
    ("agriculture", "Agriculture"),
    ("veterans", "Anciens combattants"),
    ("cantines", "Cantines"),
    ("commerce", "Commerce"),
    ("cimetières", "Cimetières"),
    ("international", "Coopération internationale"),
    ("culture", "Culture"),
    ("eau", "Eau assainissement"),
    ("égalité F/H", "Égalité F/H"),
    ("emploi", "Emploi"),
    ("environnement", "Environnement"),
    ("finances", "Finances"),
    ("handicap", "Handicap"),
    ("jeunesse", "Jeunesse"),
    ("logement", "Logement"),
    ("personnel", "Personnel"),
    ("discriminations", "Luttes contre discriminations"),
    ("personnes agées", "Personnes âgées"),
    ("petite enfance", "Petite enfance"),
    ("propreté", "Propreté"),
    ("santé", "Santé"),
    ("sécurité", "Sécurité"),
    ("sport", "Sport"),
    ("tourisme", "Tourisme"),
    ("déchets", "Traitement des déchets"),
    ("transport", "Transport"),
    ("travaux", "Travaux"),
    ("urbanisme", "Urbanisme"),
    ("associations", "Vie associative"),
    ("voirie", "Voirie"),
)

STATUT_A_VERIFIER_ADMIN = "INC"
STATUT_A_VERIFIER_INSCRIPTION = "DEM"
STATUT_VERIFIE = "INS"
STATUT_CHOICES = (
    (STATUT_A_VERIFIER_ADMIN, "Mandat à vérifier (ajouté côté admin)"),
    (
        STATUT_A_VERIFIER_INSCRIPTION,
        "Mandat à vérifier (ajouté par la personne elle-même)",
    ),
    (STATUT_VERIFIE, "Mandat vérifié"),
)


def mandat_municipal_dates_par_defaut():
    return DateRange(lower=datetime.date(2020, 3, 22), upper=datetime.date(2026, 3, 1))


def mandat_departemental_dates_par_defaut():
    return DateRange(lower=datetime.date(2015, 3, 29), upper=datetime.date(2021, 3, 31))


def mandat_regional_dates_par_defaut():
    return DateRange(
        lower=datetime.date(2015, 12, 13), upper=datetime.date(2021, 3, 31)
    )


class MandatHistoryMixin(HistoryMixin):
    def get_history_step(cls, old, new, **kwargs):
        old_fields = old.field_dict if old else {}
        new_fields = new.field_dict
        revision = new.revision
        person = revision.user.person if revision.user else None

        res = {
            "modified": revision.date_created,
            "comment": revision.get_comment(),
            "diff": cls.get_diff(old_fields, new_fields) if old_fields else [],
        }

        if person:
            res["user"] = format_html(
                '<a href="{url}">{text}</a>',
                url=reverse("admin:people_person_change", args=[person.pk]),
                text=person.get_short_name(),
            )
        else:
            res["user"] = "Utilisateur inconnu"

        if old is None:
            res["title"] = "Création"
        else:
            res["title"] = "Modification"

        return res


class UniqueWithinDates:
    def validate_unique(self, exclude=None):
        """Vérifie qu'il n'existe pas d'autre mandat avec même personne, même conseil, et plage de dates en conflit

        Ajoute une `ValidationError` dans ce cas. Deux plages de dates sont en conflits si elles se chevauchent, même
        partiellement.

        Cette unicité est assurée côté base de données par une contrainte EXCLUDE mise en place dans la migration
        `0007_plusieurs_mandats`.
        """
        try:
            super().validate_unique(exclude)
        except ValidationError as e:
            errors = e.error_dict
        else:
            errors = {}

        if exclude is None:
            exclude = []

        if not any(f in exclude for f in ["person", "conseil", "dates"]):
            qs = self.__class__._default_manager.filter(
                person_id=self.person_id,
                conseil_id=self.conseil_id,
                dates__overlap=self.dates,
            )
            model_class_pk = self._get_pk_val()
            if not self._state.adding and model_class_pk is not None:
                qs = qs.exclude(pk=model_class_pk)

            if qs.exists():
                other = qs.first()
                errors.setdefault(NON_FIELD_ERRORS, []).append(
                    ValidationError(
                        message="Il existe déjà un mandat pour cette personne et ce conseil aux mêmes dates.",
                        code="dates_overlap",
                        params={"other": other.id},
                    )
                )

        if errors:
            raise ValidationError(errors)


@reversion.register()
class MandatMunicipal(MandatHistoryMixin, UniqueWithinDates, models.Model):
    MANDAT_CONSEILLER_MAJORITE = "MAJ"
    MANDAT_CONSEILLER_OPPOSITION = "OPP"
    MANDAT_MAIRE = "MAI"
    MANDAT_MAIRE_ADJOINT = "ADJ"
    MANDAT_CONSEILLER_DELEGUE = "DEL"
    MANDAT_MAIRE_DA = "MDA"

    MANDAT_CHOICES = (
        (MANDAT_CONSEILLER_MAJORITE, "Conseiller⋅e municipal majoritaire"),
        (MANDAT_CONSEILLER_OPPOSITION, "Conseiller⋅e municipal minoritaire"),
        (MANDAT_MAIRE, "Maire"),
        (MANDAT_MAIRE_ADJOINT, "Adjoint⋅e au maire"),
        (MANDAT_CONSEILLER_DELEGUE, "Conseiller⋅e municipal délégué"),
        (MANDAT_MAIRE_DA, "Maire d'une commune déléguée ou associée"),
    )

    MANDAT_EPCI_PAS_DE_MANDAT = "NON"
    MANDAT_EPCI_MAJORITE = "MAJ"
    MANDAT_EPCI_OPPOSITION = "OPP"
    MANDAT_EPCI_PRESIDENT = "PRE"
    MANDAT_EPCI_VICE_PRESIDENT = "VPR"
    MANDAT_EPCI_CHOICES = (
        (MANDAT_EPCI_PAS_DE_MANDAT, "Pas de mandat communautaire"),
        (MANDAT_EPCI_MAJORITE, "Délégué⋅e majoritaire"),
        (MANDAT_EPCI_OPPOSITION, "Délégué⋅e minoritaire",),
        (MANDAT_EPCI_PRESIDENT, "Président"),
        (MANDAT_EPCI_VICE_PRESIDENT, "Vice-Président"),
    )

    person = models.ForeignKey(
        "people.Person", verbose_name="Élu", on_delete=models.CASCADE
    )

    conseil = models.ForeignKey(
        "data_france.Commune",
        verbose_name="Commune",
        null=False,
        on_delete=models.CASCADE,
    )

    dates = DateRangeField(
        verbose_name="Début et fin du mandat",
        help_text="La date de fin correspond à la date théorique de fin du mandat si elle est dans le futur et à la"
        " date effective sinon.",
        default=mandat_municipal_dates_par_defaut,
    )

    mandat = models.CharField(
        "Type de mandat", max_length=3, choices=MANDAT_CHOICES, blank=True
    )

    email_officiel = models.ForeignKey(
        to="people.PersonEmail",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Adresse email officielle",
        help_text="L'adresse avec laquelle contacter l'élu pour des questions officielles",
    )

    delegations_municipales = ArrayField(
        verbose_name="Délégations",
        base_field=models.CharField(max_length=20, choices=DELEGATIONS_CHOICES),
        null=False,
        blank=True,
        default=list,
    )

    communautaire = models.CharField(
        "Élu EPCI",
        max_length=3,
        choices=MANDAT_EPCI_CHOICES,
        default=MANDAT_EPCI_PAS_DE_MANDAT,
    )

    statut = models.CharField(
        "Statut", max_length=3, choices=STATUT_CHOICES, default=STATUT_A_VERIFIER_ADMIN
    )

    class Meta:
        verbose_name_plural = "Mandats municipaux"
        ordering = ("conseil", "person")

    def __str__(self):
        if hasattr(self, "person") and hasattr(self, "conseil"):
            if self.person.gender == "M":
                elu = "élu"
            elif self.person.gender == "F":
                elu = "élue"
            else:
                elu = "élu⋅e"
            return f"{self.person}, {elu} à {self.conseil.nom_complet}"

        return "Nouveau mandat municipal"


@reversion.register()
class MandatDepartemental(MandatHistoryMixin, UniqueWithinDates, models.Model):
    MANDAT_CONSEILLER_MAJORITE = "MAJ"
    MANDAT_CONSEILLER_OPPOSITION = "OPP"
    MANDAT_PRESIDENT = "PRE"
    MANDAT_VICE_PRESIDENT = "VPR"

    MANDAT_CHOICES = (
        (MANDAT_CONSEILLER_MAJORITE, "Conseiller⋅e majoritaire"),
        (MANDAT_CONSEILLER_OPPOSITION, "Conseiller⋅e minoritaire"),
        (MANDAT_PRESIDENT, "Président du conseil"),
        (MANDAT_VICE_PRESIDENT, "Vice-Président"),
    )

    person = models.ForeignKey(
        "people.Person", verbose_name="Élu", on_delete=models.CASCADE
    )

    conseil = models.ForeignKey(
        "data_france.CollectiviteDepartementale",
        verbose_name="Conseil départemental (ou de métropole)",
        null=False,
        on_delete=models.CASCADE,
    )

    dates = DateRangeField(
        verbose_name="Début et fin du mandat",
        help_text="La date de fin correspond à la date théorique de fin du mandat si elle est dans le futur et à la"
        " date effective sinon.",
        default=mandat_departemental_dates_par_defaut,
    )

    mandat = models.CharField(
        "Type de mandat", max_length=3, choices=MANDAT_CHOICES, blank=True
    )

    email_officiel = models.ForeignKey(
        to="people.PersonEmail",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Adresse email officielle",
        help_text="L'adresse avec laquelle contacter l'élu pour des questions officielles",
    )

    delegations_municipales = ArrayField(
        verbose_name="Délégations",
        base_field=models.CharField(max_length=20, choices=DELEGATIONS_CHOICES),
        null=False,
        blank=True,
        default=list,
    )

    statut = models.CharField(
        "Statut", max_length=3, choices=STATUT_CHOICES, default=STATUT_A_VERIFIER_ADMIN
    )

    class Meta:
        verbose_name = "Mandat départemental"
        verbose_name_plural = "Mandats départementaux"
        ordering = ("conseil", "person")

    def __str__(self):
        if hasattr(self, "person") and hasattr(self, "conseil"):
            if self.person.gender == "M":
                elu = "élu"
            elif self.person.gender == "F":
                elu = "élue"
            else:
                elu = "élu⋅e"
            return f"{self.person}, {elu} à {self.conseil.nom}"

        return "Nouveau mandat départemental"


@reversion.register()
class MandatRegional(MandatHistoryMixin, UniqueWithinDates, models.Model):
    MANDAT_CONSEILLER_MAJORITE = "MAJ"
    MANDAT_CONSEILLER_OPPOSITION = "OPP"
    MANDAT_PRESIDENT = "PRE"
    MANDAT_VICE_PRESIDENT = "VPR"

    MANDAT_CHOICES = (
        (MANDAT_CONSEILLER_MAJORITE, "Conseiller⋅e majoritaire"),
        (MANDAT_CONSEILLER_OPPOSITION, "Conseiller⋅e minoritaire"),
        (MANDAT_PRESIDENT, "Président du conseil"),
        (MANDAT_VICE_PRESIDENT, "Vice-Président"),
    )

    person = models.ForeignKey(
        "people.Person", verbose_name="Élu", on_delete=models.CASCADE
    )

    conseil = models.ForeignKey(
        "data_france.CollectiviteRegionale",
        verbose_name="Conseil régional (ou de collectivité unique)",
        null=False,
        on_delete=models.CASCADE,
    )

    dates = DateRangeField(
        verbose_name="Début et fin du mandat",
        help_text="La date de fin correspond à la date théorique de fin du mandat si elle est dans le futur et à la"
        " date effective sinon.",
        default=mandat_regional_dates_par_defaut,
    )

    mandat = models.CharField(
        "Type de mandat", max_length=3, choices=MANDAT_CHOICES, blank=True
    )

    email_officiel = models.ForeignKey(
        to="people.PersonEmail",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Adresse email officielle",
        help_text="L'adresse avec laquelle contacter l'élu pour des questions officielles",
    )

    delegations_municipales = ArrayField(
        verbose_name="Délégations",
        base_field=models.CharField(max_length=20, choices=DELEGATIONS_CHOICES),
        null=False,
        blank=True,
        default=list,
    )

    statut = models.CharField(
        "Statut", max_length=3, choices=STATUT_CHOICES, default=STATUT_A_VERIFIER_ADMIN
    )

    class Meta:
        verbose_name = "Mandat régional"
        verbose_name_plural = "Mandats régionaux"
        ordering = ("conseil", "person")

    def __str__(self):
        if hasattr(self, "person") and hasattr(self, "conseil"):
            if self.person.gender == "M":
                elu = "élu"
            elif self.person.gender == "F":
                elu = "élue"
            else:
                elu = "élu⋅e"
            return f"{self.person}, {elu} à {self.conseil.nom}"

        return "Nouveau mandat départemental"
