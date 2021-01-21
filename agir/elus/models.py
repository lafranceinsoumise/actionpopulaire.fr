from datetime import date

import reversion
from django.contrib.gis.db.models.functions import Distance
from django.contrib.postgres.fields import ArrayField, DateRangeField
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.db import models, connection
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.html import format_html
from psycopg2._range import DateRange

from agir.lib.display import genrer
from agir.lib.history import HistoryMixin

MUNICIPAL_DEFAULT_DATE_RANGE = DateRange(date(2020, 6, 28), date(2026, 3, 31))
DEPARTEMENTAL_DEFAULT_DATE_RANGE = DateRange(date(2015, 3, 29), date(2021, 3, 31))
REGIONAL_DEFAULT_DATE_RANGE = DateRange(date(2015, 12, 13), date(2021, 3, 31))

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
    ("ess", "Économie sociale et solidaire"),
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
STATUT_A_VERIFIER_IMPORT = "IMP"
STATUT_FAUX_POSITIF_IMPORT = "FXP"
STATUT_VERIFIE = "INS"
STATUT_CHOICES = (
    (STATUT_A_VERIFIER_ADMIN, "Mandat à vérifier (ajouté côté admin)"),
    (
        STATUT_A_VERIFIER_INSCRIPTION,
        "Mandat à vérifier (ajouté par la personne elle-même)",
    ),
    (STATUT_A_VERIFIER_IMPORT, "Importé par une opération automatique"),
    (STATUT_FAUX_POSITIF_IMPORT, "Faux-positif dans une opération d'import"),
    (STATUT_VERIFIE, "Mandat vérifié"),
)


class MandatQueryset(models.QuerySet):
    def annotate_distance(self):
        return self.annotate(
            distance=Distance(
                models.F("person__coordinates"), models.F("conseil__geometry")
            )
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
        `0008_plusieurs_mandats`.
        """
        try:
            super().validate_unique(exclude)
        except ValidationError as e:
            errors = e.error_dict
        else:
            errors = {}

        if exclude is None:
            exclude = []

        unique_fields_names = ["person", "conseil", "dates"]
        all_excluded = all(f in exclude for f in unique_fields_names)
        any_is_none = any(getattr(self, f, None) is None for f in unique_fields_names)

        if not (all_excluded or any_is_none):
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


class MandatAbstrait(UniqueWithinDates, MandatHistoryMixin, models.Model):
    objects = MandatQueryset.as_manager()

    person = models.ForeignKey(
        "people.Person", verbose_name="Élu", on_delete=models.CASCADE
    )

    dates = DateRangeField(
        verbose_name="Début et fin du mandat",
        help_text="La date de fin correspond à la date théorique de fin du mandat si elle est dans le futur et à la"
        " date effective sinon.",
    )

    email_officiel = models.ForeignKey(
        to="people.PersonEmail",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Adresse email officielle",
        help_text="L'adresse avec laquelle contacter l'élu pour des questions officielles",
    )

    statut = models.CharField(
        "Statut",
        max_length=3,
        choices=STATUT_CHOICES,
        default=STATUT_A_VERIFIER_ADMIN,
        help_text="Indique la qualité de l'information sur cet⋅te élu⋅e, indépendamment des questions politiques et de"
        " son appartenance au réseau des élus. Une valeur « Vérifié » signifie que : 1) il a été vérifié que le mandat"
        " existe réellement et 2) le compte éventuellement associé appartient bien à la personne élue.",
    )

    def besoin_validation_personne(self):
        return self.statut in [STATUT_A_VERIFIER_IMPORT, STATUT_A_VERIFIER_ADMIN]

    def actif(self):
        return timezone.now().date() in self.dates

    @cached_property
    def distance(self):
        return (
            self._meta.default_manager.annotate_distance()
            .values("distance")
            .get(pk=self.id)["distance"]
        )

    @property
    def nom_conseil(self):
        return self.conseil.nom

    class Meta:
        abstract = True


@reversion.register()
class MandatMunicipal(MandatAbstrait):
    MANDAT_INCONNU = "INC"
    MANDAT_CONSEILLER_MAJORITE = "MAJ"
    MANDAT_CONSEILLER_OPPOSITION = "OPP"
    MANDAT_MAIRE = "MAI"
    MANDAT_MAIRE_ADJOINT = "ADJ"
    MANDAT_MAIRE_DA = "MDA"

    MANDAT_CHOICES = (
        (MANDAT_INCONNU, "Situation au conseil inconnue"),
        (MANDAT_CONSEILLER_MAJORITE, "Conseiller⋅e municipal⋅e majoritaire"),
        (MANDAT_CONSEILLER_OPPOSITION, "Conseiller⋅e municipal⋅e minoritaire"),
        (MANDAT_MAIRE, "Maire"),
        (MANDAT_MAIRE_ADJOINT, "Adjoint⋅e au maire"),
        (MANDAT_MAIRE_DA, "Maire d'une commune déléguée ou associée"),
    )

    MANDAT_EPCI_PAS_DE_MANDAT = "NON"
    MANDAT_EPCI_MANDAT_INCONNU = "INC"
    MANDAT_EPCI_MAJORITE = "MAJ"
    MANDAT_EPCI_OPPOSITION = "OPP"
    MANDAT_EPCI_PRESIDENT = "PRE"
    MANDAT_EPCI_VICE_PRESIDENT = "VPR"
    MANDAT_EPCI_CHOICES = (
        (MANDAT_EPCI_PAS_DE_MANDAT, "Pas de mandat communautaire"),
        (MANDAT_EPCI_MANDAT_INCONNU, "Délégué⋅e, situation inconnue"),
        (MANDAT_EPCI_MAJORITE, "Délégué⋅e majoritaire"),
        (MANDAT_EPCI_OPPOSITION, "Délégué⋅e minoritaire"),
        (MANDAT_EPCI_PRESIDENT, "Président"),
        (MANDAT_EPCI_VICE_PRESIDENT, "Vice-Président"),
    )

    reference = models.ForeignKey(
        "data_france.EluMunicipal",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Référence dans le RNE",
        help_text="La fiche correspondant à cet élu dans le Répertoire National des Élus",
    )

    person = models.ForeignKey(
        "people.Person",
        verbose_name="Élu",
        on_delete=models.CASCADE,
        related_name="mandats_municipaux",
        related_query_name="mandat_municipal",
    )

    conseil = models.ForeignKey(
        "data_france.Commune",
        verbose_name="Commune",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    mandat = models.CharField(
        "Type de mandat",
        max_length=3,
        choices=MANDAT_CHOICES,
        blank=False,
        default=MANDAT_INCONNU,
    )

    delegations = ArrayField(
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

    def __init__(self, *args, **kwargs):
        self._meta.get_field("dates").default = MUNICIPAL_DEFAULT_DATE_RANGE
        super().__init__(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Mandats municipaux"
        ordering = ("conseil", "person")

    def __str__(self):
        if hasattr(self, "person") and hasattr(self, "conseil"):
            if self.conseil is None:
                return f"{self.person}, {genrer(self.person.gender, 'élu⋅e')} {genrer(self.person.gender, 'municipal⋅e')} (commune inconnue)"
            return f"{self.person}, {genrer(self.person.gender, 'élu⋅e')} à {self.conseil.nom_complet}"

        return "Nouveau mandat municipal"

    def titre_complet(self, conseil_avant=False):
        if self.mandat in [
            self.MANDAT_INCONNU,
            self.MANDAT_CONSEILLER_MAJORITE,
            self.MANDAT_CONSEILLER_OPPOSITION,
        ]:
            titre = genrer(self.person.gender, "Conseiller⋅ère municipal⋅e")
            titre += {
                self.MANDAT_CONSEILLER_MAJORITE: " majoritaire",
                self.MANDAT_CONSEILLER_OPPOSITION: " minoritaire",
            }.get(self.mandat, "")
        elif self.mandat == self.MANDAT_MAIRE_ADJOINT:
            titre = f"{genrer(self.person.gender, 'Adjoint⋅e')} au maire"
        else:
            titre = self.get_mandat_display()

        if self.conseil is None:
            return titre

        if conseil_avant:
            return f"{self.conseil.nom_complet}, {titre}"
        return f"{titre} {self.conseil.nom_avec_charniere}"

    def get_absolute_url(self):
        return reverse(
            viewname="elus:modifier_mandat_municipal", kwargs={"pk": self.id},
        )

    def get_delete_url(self):
        return reverse(
            viewname="elus:supprimer_mandat_municipal", kwargs={"pk": self.id},
        )


@reversion.register()
class MandatDepartemental(MandatAbstrait):
    MANDAT_INCONNU = "INC"
    MANDAT_CONSEILLER_MAJORITE = "MAJ"
    MANDAT_CONSEILLER_OPPOSITION = "OPP"
    MANDAT_PRESIDENT = "PRE"
    MANDAT_VICE_PRESIDENT = "VPR"

    MANDAT_CHOICES = (
        (MANDAT_INCONNU, "Situation au conseil inconnue"),
        (MANDAT_CONSEILLER_MAJORITE, "Conseiller⋅e majoritaire"),
        (MANDAT_CONSEILLER_OPPOSITION, "Conseiller⋅e minoritaire"),
        (MANDAT_PRESIDENT, "Président"),
        (MANDAT_VICE_PRESIDENT, "Vice-Président"),
    )

    person = models.ForeignKey(
        "people.Person",
        verbose_name="Élu",
        on_delete=models.CASCADE,
        related_name="mandats_departementaux",
        related_query_name="mandat_departemental",
    )

    conseil = models.ForeignKey(
        "data_france.CollectiviteDepartementale",
        verbose_name="Conseil départemental (ou de métropole)",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    mandat = models.CharField(
        "Type de mandat",
        max_length=3,
        choices=MANDAT_CHOICES,
        blank=False,
        default=MANDAT_INCONNU,
    )

    delegations = ArrayField(
        verbose_name="Délégations",
        base_field=models.CharField(max_length=20, choices=DELEGATIONS_CHOICES),
        null=False,
        blank=True,
        default=list,
    )

    def __init__(self, *args, **kwargs):
        self._meta.get_field("dates").default = DEPARTEMENTAL_DEFAULT_DATE_RANGE
        super().__init__(*args, **kwargs)

    class Meta:
        verbose_name = "Mandat départemental"
        verbose_name_plural = "Mandats départementaux"
        ordering = ("conseil", "person")

    def __str__(self):
        if hasattr(self, "person") and hasattr(self, "conseil"):
            if self.conseil is None:
                return f"{self.person}, {genrer(self.person.gender, 'élu⋅e')} {genrer(self.person.gender, 'départemental⋅e')} (lieu inconnu)"
            return f"{self.person}, {genrer(self.person.gender, 'élu.e')} au {self.conseil.nom}"

        return "Nouveau mandat départemental"

    def titre_complet(self, conseil_avant=False):
        if self.mandat in [
            self.MANDAT_INCONNU,
            self.MANDAT_CONSEILLER_MAJORITE,
            self.MANDAT_CONSEILLER_OPPOSITION,
        ]:
            titre = genrer(self.person.gender, "Conseiller⋅ère")
            titre += {
                self.MANDAT_CONSEILLER_MAJORITE: " majoritaire",
                self.MANDAT_CONSEILLER_OPPOSITION: " minoritaire",
            }.get(self.mandat, "")
        elif self.mandat == self.MANDAT_VICE_PRESIDENT:
            titre = genrer(self.person.gender, "Vice-président⋅e")
        else:
            titre = self.get_mandat_display()

        if self.conseil is None:
            return titre

        if conseil_avant:
            return f"{self.conseil.nom}, {titre}"
        return f"{titre} au {self.conseil.nom}"

    def get_absolute_url(self):
        return reverse(
            viewname="elus:modifier_mandat_departemental", kwargs={"pk": self.id},
        )

    def get_delete_url(self):
        return reverse(
            viewname="elus:supprimer_mandat_departemental", kwargs={"pk": self.id},
        )


@reversion.register()
class MandatRegional(MandatAbstrait):
    MANDAT_INCONNU = "INC"
    MANDAT_CONSEILLER_MAJORITE = "MAJ"
    MANDAT_CONSEILLER_OPPOSITION = "OPP"
    MANDAT_PRESIDENT = "PRE"
    MANDAT_VICE_PRESIDENT = "VPR"

    MANDAT_CHOICES = (
        (MANDAT_INCONNU, "Situation au conseil inconnue"),
        (MANDAT_CONSEILLER_MAJORITE, "Conseiller⋅e majoritaire"),
        (MANDAT_CONSEILLER_OPPOSITION, "Conseiller⋅e minoritaire"),
        (MANDAT_PRESIDENT, "Président"),
        (MANDAT_VICE_PRESIDENT, "Vice-Président"),
    )

    person = models.ForeignKey(
        "people.Person",
        verbose_name="Élu",
        on_delete=models.CASCADE,
        related_name="mandats_regionaux",
        related_query_name="mandat_regional",
    )

    conseil = models.ForeignKey(
        "data_france.CollectiviteRegionale",
        verbose_name="Conseil régional (ou de collectivité unique)",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    mandat = models.CharField(
        "Type de mandat",
        max_length=3,
        choices=MANDAT_CHOICES,
        blank=False,
        default=MANDAT_INCONNU,
    )

    delegations = ArrayField(
        verbose_name="Délégations",
        base_field=models.CharField(max_length=20, choices=DELEGATIONS_CHOICES),
        null=False,
        blank=True,
        default=list,
    )

    def __init__(self, *args, **kwargs):
        self._meta.get_field("dates").default = REGIONAL_DEFAULT_DATE_RANGE
        super().__init__(*args, **kwargs)

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
                if self.conseil is None:
                    return f"{self.person}, {genrer(self.person.gender, 'élu⋅e')} {genrer(self.person.gender, 'régional⋅e')} (lieu inconnu)"
            return f"{self.person}, {elu} au {self.conseil.nom}"

        return "Nouveau mandat régional"

    def titre_complet(self, conseil_avant=False):
        if self.mandat in [
            self.MANDAT_INCONNU,
            self.MANDAT_CONSEILLER_MAJORITE,
            self.MANDAT_CONSEILLER_OPPOSITION,
        ]:
            titre = genrer(self.person.gender, "Conseiller⋅ère")
            titre += {
                self.MANDAT_CONSEILLER_MAJORITE: " majoritaire",
                self.MANDAT_CONSEILLER_OPPOSITION: " minoritaire",
            }.get(self.mandat, "")
        elif self.mandat == self.MANDAT_VICE_PRESIDENT:
            titre = genrer(self.person.gender, "Vice-président⋅e")
        else:
            titre = self.get_mandat_display()

        if self.conseil is None:
            return titre

        nom_conseil = self.conseil.nom

        if conseil_avant:
            return f"{nom_conseil}, {titre}"

        if nom_conseil.startswith("Assemblée"):
            return f"{titre} à l'{nom_conseil}"

        return f"{titre} au {nom_conseil}"

    def get_absolute_url(self):
        return reverse(
            viewname="elus:modifier_mandat_regional", kwargs={"pk": self.id},
        )

    def get_delete_url(self):
        return reverse(
            viewname="elus:supprimer_mandat_regional", kwargs={"pk": self.id},
        )


types_elus = {
    "maire": MandatMunicipal,
    "municipal": MandatMunicipal,
    "departemental": MandatDepartemental,
    "regional": MandatRegional,
}
