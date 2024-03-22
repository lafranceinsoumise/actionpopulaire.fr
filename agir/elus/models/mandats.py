from datetime import date

import reversion
from data_france.models import CollectiviteRegionale
from django.contrib.gis.db.models.functions import Distance
from django.contrib.postgres.fields import DateRangeField, ArrayField
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.html import format_html
from psycopg2._range import DateRange

from agir.lib.display import genrer
from agir.lib.history import HistoryMixin

__all__ = [
    "MandatMunicipal",
    "MandatDepartemental",
    "MandatRegional",
    "MandatDepute",
    "MandatDeputeEuropeen",
    "MandatConsulaire",
    "StatutMandat",
    "types_elus",
    "DELEGATIONS_CHOICES",
]


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


class StatutMandat(models.TextChoices):
    CONTACT_NECESSAIRE = "INC", "Personne à contacter"
    INSCRIPTION_VIA_PROFIL = "DEM", "Mandat ajouté par la personne via son profil"
    IMPORT_AUTOMATIQUE = "IMP", "Importé par une opération automatique"
    FAUX = "FXP", "Faux-positif ou fausse déclaration"
    CONFIRME = "INS", "Mandat vérifié et confirmé"


class MandatQueryset(models.QuerySet):
    def annotate_distance(self):
        return self.annotate(
            distance=Distance(
                models.F("person__coordinates"), models.F("conseil__geometry")
            )
        )

    def confirmes(self):
        return self.filter(statut=StatutMandat.CONFIRME)

    def potentiels(self):
        return self.exclude(statut=StatutMandat.FAUX)

    def actifs(self):
        return self.filter(dates__contains=timezone.now())


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
        choices=StatutMandat.choices,
        default=StatutMandat.CONTACT_NECESSAIRE,
        help_text="Indique la qualité de l'information sur cet⋅te élu⋅e, indépendamment des questions politiques et de"
        " son appartenance au réseau des élus. Une valeur « Vérifié » signifie que : 1) il a été vérifié que le mandat"
        " existe réellement et 2) le compte éventuellement associé appartient bien à la personne élue.",
    )

    def besoin_validation_personne(self):
        """Indique que le mandat n'a pas été validé par la personne concernée elle-même."""
        return self.statut in [
            StatutMandat.IMPORT_AUTOMATIQUE,
            StatutMandat.CONTACT_NECESSAIRE,
        ]

    def actif(self):
        return timezone.now().date() in self.dates

    def passe(self):
        return timezone.now().date() >= self.dates.upper

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

    def as_json(self):
        return {
            "id": self.id,
            "statut": self.get_statut_display(),
            "dates": [self.dates.lower, self.dates.upper],
            "email_officiel": self.email_officiel and self.email_officiel.address,
        }

    class Meta:
        abstract = True


@reversion.register()
class MandatMunicipal(MandatAbstrait):
    DEFAULT_DATE_RANGE = DateRange(date(2020, 6, 28), date(2026, 3, 31))

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
        related_name="elus",
        related_query_name="elu",
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

    class Meta:
        verbose_name_plural = "Mandats municipaux"
        ordering = ("conseil", "person")

    def as_json(self):
        return {
            **super().as_json(),
            "type": "municipal",
            "commune": self.nom_conseil,
            "mandat": self.get_mandat_display(),
            "communautaire": self.get_communautaire_display(),
        }

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
            if self.conseil and (self.conseil.code == "75056"):
                # cas spécial de paris :
                titre = genrer(self.person.gender, "conseiller⋅ère")
            else:
                titre = genrer(self.person.gender, "Conseiller⋅ère municipal⋅e")
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
            viewname="elus:modifier_mandat_municipal",
            kwargs={"pk": self.id},
        )

    def get_delete_url(self):
        return reverse(
            viewname="elus:supprimer_mandat_municipal",
            kwargs={"pk": self.id},
        )


@reversion.register()
class MandatDepartemental(MandatAbstrait):
    DEFAULT_DATE_RANGE = DateRange(date(2021, 7, 1), date(2027, 3, 31))

    MANDAT_INCONNU = "INC"
    MANDAT_CONSEILLER_MAJORITE = "MAJ"
    MANDAT_CONSEILLER_OPPOSITION = "OPP"
    MANDAT_PRESIDENT = "PRE"
    MANDAT_VICE_PRESIDENT = "VPR"

    MANDAT_CHOICES = (
        (MANDAT_INCONNU, "Situation au conseil inconnue"),
        (MANDAT_CONSEILLER_MAJORITE, "Conseiller⋅e majoritaire"),
        (MANDAT_CONSEILLER_OPPOSITION, "Conseiller⋅e minoritaire"),
        (MANDAT_PRESIDENT, "Président⋅e"),
        (MANDAT_VICE_PRESIDENT, "Vice-Président⋅e"),
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

    reference = models.ForeignKey(
        "data_france.EluDepartemental",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Référence dans le RNE",
        help_text="La fiche correspondant à cet élu dans le Répertoire National des Élus",
        related_name="elus",
        related_query_name="elu",
    )

    class Meta:
        verbose_name = "Mandat départemental"
        verbose_name_plural = "Mandats départementaux"
        ordering = ("conseil", "person")

    def as_json(self):
        return {
            **super().as_json(),
            "type": "départemental",
            "département": self.nom_conseil,
            "mandat": self.get_mandat_display(),
        }

    def __str__(self):
        if self.person is not None:
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
        else:
            titre = genrer(self.person.gender, self.get_mandat_display())

        if self.conseil is None:
            return titre

        if conseil_avant:
            return f"{self.conseil.nom}, {titre}"
        return f"{titre} {self.conseil.nom_avec_charniere}"

    def get_absolute_url(self):
        return reverse(
            viewname="elus:modifier_mandat_departemental",
            kwargs={"pk": self.id},
        )

    def get_delete_url(self):
        return reverse(
            viewname="elus:supprimer_mandat_departemental",
            kwargs={"pk": self.id},
        )


@reversion.register()
class MandatRegional(MandatAbstrait):
    DEFAULT_DATE_RANGE = DateRange(date(2021, 7, 1), date(2027, 3, 31))

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

    reference = models.ForeignKey(
        "data_france.EluRegional",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Référence dans le RNE",
        help_text="La fiche correspondant à cet élu dans le Répertoire National des Élus",
        related_name="elus",
        related_query_name="elu",
    )

    class Meta:
        verbose_name = "Mandat régional"
        verbose_name_plural = "Mandats régionaux"
        ordering = ("conseil", "person")

    def as_json(self):
        return {
            **super().as_json(),
            "type": "régional",
            "région": self.nom_conseil,
            "mandat": self.get_mandat_display(),
        }

    def __str__(self):
        if self.person:
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
        ctu = (
            self.conseil
            and self.conseil.type == CollectiviteRegionale.TYPE_COLLECTIVITE_UNIQUE
        )

        if self.mandat in [
            self.MANDAT_INCONNU,
            self.MANDAT_CONSEILLER_MAJORITE,
            self.MANDAT_CONSEILLER_OPPOSITION,
        ]:
            if ctu:
                titre = genrer(self.person.gender, "Conseiller⋅ère")
            else:
                titre = genrer(self.person.gender, "Conseiller⋅ère régional⋅e")
        else:
            qualif = "" if ctu else " du conseil régional"
            titre = genrer(
                self.person.gender,
                f"{self.get_mandat_display()}{qualif}",
            )

        if self.conseil is None:
            return titre

        nom_conseil = self.conseil.nom

        if conseil_avant:
            return f"{nom_conseil}, {titre}"

        if nom_conseil.startswith("Assemblée"):
            return f"{titre} à l'{nom_conseil}"

        return f"{titre} de {nom_conseil}"

    def get_absolute_url(self):
        return reverse(
            viewname="elus:modifier_mandat_regional",
            kwargs={"pk": self.id},
        )

    def get_delete_url(self):
        return reverse(
            viewname="elus:supprimer_mandat_regional",
            kwargs={"pk": self.id},
        )


@reversion.register()
class MandatConsulaire(MandatAbstrait):
    DEFAULT_DATE_RANGE = DateRange(date(2021, 6, 1), date(2027, 5, 31))

    class Mandat(models.TextChoices):
        CONSEILLER = "C", "Conseiller⋅ère consulaire"
        MEMBRE_AFE = "M", "Conseiller⋅ère consulaire et membre de l'AFE"
        DELEGUE = "D", "Délégué⋅e consulaire"

    person = models.ForeignKey(
        "people.Person",
        verbose_name="Élu",
        on_delete=models.CASCADE,
        related_name="mandats_consulaires",
        related_query_name="mandat_consulaire",
    )

    conseil = models.ForeignKey(
        "data_france.CirconscriptionConsulaire",
        verbose_name="Circonscription consulaire",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    mandat = models.CharField(
        verbose_name="Mandat",
        max_length=1,
        blank=False,
        choices=Mandat.choices,
        default=Mandat.CONSEILLER,
    )

    def __str__(self):
        if self.person:
            if self.conseil is None:
                return f"{self.person}, {genrer(self.person.gender, self.get_mandat_display())} (circonscription inconnue)"
            return f"{self.person}, {genrer(self.person.gender, self.get_mandat_display())} ({self.conseil.nom})"

        return "Nouveau mandat consulaire"

    def as_json(self):
        return {
            **super().as_json(),
            "type": "consulaire",
            "circonscription": self.nom_conseil,
            "mandat": self.get_mandat_display(),
        }

    def titre_complet(self, conseil_avant=False):
        titre = genrer(self.person.gender, self.get_mandat_display())
        conseil = (
            self.conseil.nom
            if self.conseil
            else "Circonscription consulaire non renseignée"
        )

        if conseil_avant:
            return f"{conseil}, {titre}"
        return f"{titre} ({conseil})"

    def get_absolute_url(self):
        return reverse(
            viewname="elus:modifier_mandat_consulaire",
            kwargs={"pk": self.id},
        )

    def get_delete_url(self):
        return reverse(
            viewname="elus:supprimer_mandat_consulaire",
            kwargs={"pk": self.id},
        )

    class Meta:
        verbose_name_plural = "mandats consulaires"


@reversion.register()
class MandatDepute(MandatAbstrait):
    DEFAULT_DATE_RANGE = DateRange(date(2022, 6, 22), date(2027, 6, 21))

    person = models.ForeignKey(
        "people.Person",
        verbose_name="Élu",
        on_delete=models.CASCADE,
        related_name="mandats_deputes",
        related_query_name="mandat_depute",
    )

    conseil = models.ForeignKey(
        "data_france.CirconscriptionLegislative",
        verbose_name="Circonscription",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    reference = models.ForeignKey(
        "data_france.Depute",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Référence dans les données AN",
        help_text="La fiche correspondant à cet élu dans la base de l'AN",
        related_name="elus",
        related_query_name="elu",
    )

    def titre_complet(self, conseil_avant=False):
        titre = genrer(self.person.gender, "député⋅e")

        if not self.conseil:
            circo = "circonscription inconnue"
        else:
            circo = str(self.conseil)

        if conseil_avant:
            return f"{circo}, {titre}"

        return f"{titre} de la {circo}"

    def __str__(self):
        return f"{self.person}, {self.titre_complet()}"

    def as_json(self):
        return {
            **super().as_json(),
            "type": "assemblée nationale",
            "circonscription": self.nom_conseil,
        }

    class Meta:
        verbose_name = "Mandat de député⋅e"
        verbose_name_plural = "Mandats de député⋅e"
        ordering = ("person", "conseil")


@reversion.register()
class MandatDeputeEuropeen(MandatAbstrait):
    DEFAULT_DATE_RANGE = DateRange(date(2019, 6, 1), date(2024, 5, 31))

    person = models.ForeignKey(
        "people.Person",
        verbose_name="Élu",
        on_delete=models.CASCADE,
        related_name="mandats_deputes_europeens",
        related_query_name="mandat_depute_depute_europeen",
    )

    reference = models.ForeignKey(
        "data_france.DeputeEuropeen",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Référence dans les données du RNE",
        help_text="La fiche correspondant à cet élu dans le répertoire national des élus",
        related_name="elus",
        related_query_name="elu",
    )

    def titre_complet(self, conseil_avant=False):
        return genrer(
            self.person.gender, "député européen", "députée européenne", "député"
        )

    def as_json(self):
        return {
            **super().as_json(),
            "type": "parlement européen",
        }

    class Meta:
        verbose_name = "Mandat de député⋅e européen⋅ne"
        verbose_name_plural = "Mandats de député⋅e européen⋅ne"
        ordering = ("person",)


types_elus = {
    "municipal": MandatMunicipal,
    "departemental": MandatDepartemental,
    "regional": MandatRegional,
    "consulaire": MandatConsulaire,
    "depute": MandatDepute,
    "depute_europeen": MandatDeputeEuropeen,
}


# Le champ `dates` des modèles de mandat est défini sur la classe `MandatAbstrait`.
# Comme les mandats ont des valeurs par défaut différentes, on ajuste cette valeur
# par défaut ici (plutôt que d'avoir à redéfinir entièrement le champ sur chacun des
# modèles concrets).
for model in types_elus.values():
    model._meta.get_field("dates").default = model.DEFAULT_DATE_RANGE
