from functools import reduce
from itertools import combinations
from operator import and_

import reversion
from django.contrib.postgres.search import SearchVectorField
from django.core.exceptions import ValidationError
from django.db import models
from dynamic_filenames import FilePattern
from phonenumber_field.modelfields import PhoneNumberField

from agir.lib.models import TimeStampedModel
from agir.lib.search import PrefixSearchQuery

__all__ = [
    "StatutRechercheParrainage",
    "RechercheParrainage",
    "AccesApplicationParrainages",
    "CHAMPS_ELUS_PARRAINAGES",
]


formulaire_parrainage_pattern = FilePattern(
    filename_pattern="elus/parrainages/{uuid:.30base32}{ext}"
)

CHAMPS_ELUS_PARRAINAGES = [
    "maire",
    "elu_departemental",
    "elu_regional",
    "depute",
    "depute_europeen",
]


class StatutRechercheParrainage(models.IntegerChoices):
    EN_COURS = 1, "En cours"
    ANNULEE = 5, "Recherche annulée"

    ENGAGEMENT = 2, "S'engage à parrainer"
    REFUS = 4, "Refuse de parrainer"
    NE_SAIT_PAS = 6, "Pas encore décidé"
    AUTRE_ENGAGEMENT = 7, "S'est engagé envers un autre candidat"

    VALIDEE = 3, "Promesse reçue et validée"
    VALIDEE_CC = 8, "Parrainage confirmé par le CC"
    AUTRE_CC = 9, "A parrainé un autre candidat"

    REVENU_SUR_ENGAGEMENT = 10, "Revenu sur son engagement"


class RechercheParrainageQueryset(models.QuerySet):
    def bloquant(self):
        return self.exclude(statut=RechercheParrainage.Statut.ANNULEE)

    def rechercher(self, query):
        return self.filter(search=PrefixSearchQuery(query, config="data_france_search"))


class RechercheParrainage(TimeStampedModel):
    objects = RechercheParrainageQueryset.as_manager()

    Statut = StatutRechercheParrainage

    maire = models.ForeignKey(
        to="data_france.EluMunicipal",
        verbose_name="Maire",
        on_delete=models.SET_NULL,
        related_name="parrainages",
        related_query_name="parrainage",
        null=True,
        blank=True,
    )
    elu_departemental = models.ForeignKey(
        to="data_france.EluDepartemental",
        verbose_name="Élu·e départemental·e",
        on_delete=models.SET_NULL,
        related_name="parrainages",
        related_query_name="parrainage",
        null=True,
        blank=True,
    )
    elu_regional = models.ForeignKey(
        to="data_france.EluRegional",
        verbose_name="Élu·e régional·e",
        on_delete=models.SET_NULL,
        related_name="parrainages",
        related_query_name="parrainage",
        null=True,
        blank=True,
    )
    depute = models.ForeignKey(
        to="data_france.Depute",
        verbose_name="Député·e",
        on_delete=models.SET_NULL,
        related_name="parrainages",
        related_query_name="parrainage",
        null=True,
        blank=True,
    )
    depute_europeen = models.ForeignKey(
        to="data_france.DeputeEuropeen",
        verbose_name="Député·e européen·e",
        on_delete=models.SET_NULL,
        related_name="parrainages",
        related_query_name="parrainage",
        null=True,
        blank=True,
    )

    person = models.ForeignKey(
        to="people.Person",
        verbose_name="Démarcheur⋅se",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    statut = models.IntegerField(choices=Statut.choices, default=Statut.EN_COURS)

    commentaires = models.TextField(
        verbose_name="Commentaires",
        blank=True,
        help_text="Commentaires saisis par la personne à l'origine de la démarche. Si vous les modifiez, "
        "ils seront visibles par la personne qui a effectué la démarche.",
    )

    commentaires_admin = models.TextField(
        verbose_name="Commentaires supplémentaires",
        blank=True,
        help_text="Tout commentaire additionnel sur le parrainage. "
        "Ces  commentaires ne sont pas visibles par la personne qui a effectué la démarche.",
    )

    formulaire = models.FileField(
        verbose_name="Formulaire de promesse signé",
        upload_to=formulaire_parrainage_pattern,
        null=True,
        blank=True,
    )

    email = models.EmailField(
        verbose_name="Adresse email",
        blank=True,
        help_text="Adresse email à utiliser pour contacter cet élu en lien avec ce parrainage.",
    )

    telephone = PhoneNumberField(
        verbose_name="Numéro de téléphone",
        blank=True,
        help_text="Numéro à utiliser pour contacter cet élu en lien avec ce parrainage.",
    )

    adresse_postale = models.TextField(
        verbose_name="Adresse postale complète",
        blank=True,
        help_text="Indiquez l'adresse postale complète (à l'exception du nom de la personne), exactement comme vous "
        "l'indiqueriez sur une enveloppe.",
    )

    parrainage = models.CharField(
        verbose_name="Parrainage effectif en 2022",
        blank=True,
        editable=False,
        max_length=250,
        help_text="Si l'élu a déjà envoyé son parrainage au Conseil Constitutionnel, pour qui l'a-t-il fait ?",
    )

    search = SearchVectorField(verbose_name="Champ de recherche", null=True)

    def validate_unique(self, exclude=None):
        try:
            super(RechercheParrainage, self).validate_unique(exclude=exclude)
        except ValidationError as exc:
            errors = exc.error_dict
        else:
            errors = {}

        if t := self.type_elu:
            if (
                RechercheParrainage.objects.filter(**{t: getattr(self, t)})
                .exclude(statut=RechercheParrainage.Statut.ANNULEE)
                .exclude(id=self.id)
                .exists()
            ):
                errors.setdefault(self.type_elu, []).append(
                    ValidationError(
                        message="Il existe déjà une fiche pour cet élu !", code="unique"
                    )
                )

        if errors:
            raise ValidationError(errors)

    @property
    def type_elu(self):
        try:
            return next(
                f for f in CHAMPS_ELUS_PARRAINAGES if getattr(self, f) is not None
            )
        except StopIteration:
            return None

    def __str__(self):
        type = self.type_elu
        nom_elu = getattr(self, type) if type else "Élu·e inconnu·e"

        return f"{nom_elu} — {self.get_statut_display().lower()}"

    @classmethod
    def trouver_parrainage(cls, obj):
        ref_model = obj._meta.get_field("reference").related_model
        field = next(
            f.name
            for f in cls._meta.get_fields()
            if isinstance(f, models.ForeignKey) and f.related_model is ref_model
        )
        return cls.objects.exclude(statut=cls.Statut.ANNULEE).get(
            **{f"{field}__elu": obj.id}
        )

    def save(self, **kwargs):
        if "update_fields" not in kwargs or any(
            f in kwargs["update_fields"] for f in CHAMPS_ELUS_PARRAINAGES
        ):
            type = self.type_elu
            if type:
                self.search = getattr(self, type).search
            else:
                self.search = None
        super().save(**kwargs)

    class Meta:
        verbose_name = "Parrainages pour la présidentielle"
        verbose_name_plural = "Parrainages pour la présidentielle"

        permissions = [
            ("acces_parrainages", "Donne l'accès à l'interface de parrainage")
        ]

        constraints = [
            # TODO: tester le comportement des contraintes uniques par rapport aux NULL
            # On veut une contrainte unique par type de mandat qui peut être pointé
            # à noter que Postgresql ne pose pas de problème avec les valeurs NULL, qui sont considérées comme
            # distinctes.
            *(
                models.UniqueConstraint(
                    name=f"parrainage_un_seul_actif_{f}",
                    fields=[f],
                    condition=~models.Q(statut=StatutRechercheParrainage.ANNULEE),
                )
                for f in CHAMPS_ELUS_PARRAINAGES
            ),
            # on ne veut pas que deux types de mandats soient pointés en même temps par une même
            # instance de parrainage
            models.CheckConstraint(
                check=reduce(
                    and_,
                    (
                        ~models.Q(**{f"{a}__isnull": False, f"{b}__isnull": False})
                        for a, b in combinations(CHAMPS_ELUS_PARRAINAGES, 2)
                    ),
                ),
                name="parrainage_un_seul_elu",
            ),
        ]


class AccesApplicationParrainagesQueryset(models.QuerySet):
    def search(self, query):
        return self.filter(
            person__search=PrefixSearchQuery(query, config="simple_unaccented")
        )


@reversion.register()
class AccesApplicationParrainages(models.Model):
    objects = AccesApplicationParrainagesQueryset.as_manager()

    class Etat(models.TextChoices):
        EN_ATTENTE = "A", "En attente"
        VALIDE = "V", "Validée"
        REFUSE = "R", "Refusée"

    person = models.OneToOneField(
        to="people.Person",
        on_delete=models.CASCADE,
        null=False,
        related_name="acces_application_parrainages",
    )
    etat = models.CharField(
        verbose_name="État de la demande",
        max_length=1,
        blank=False,
        choices=Etat.choices,
        default=Etat.EN_ATTENTE,
    )

    class Meta:
        verbose_name = verbose_name_plural = (
            "Accès à l'application de recherches de parrainages"
        )
        ordering = ("etat", "person")

    def __str__(self):
        return f"Accès {self.get_etat_display().lower()} pour {self.person}"
