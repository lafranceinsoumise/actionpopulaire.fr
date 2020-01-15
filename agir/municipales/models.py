from django.contrib.gis.db.models import MultiPolygonField
from django.contrib.postgres.search import SearchVector, SearchRank
from django.db import models
from django.db.models import UniqueConstraint

from agir.lib.model_fields import FacebookPageField, TwitterProfileField
from agir.lib.models import TimeStampedModel
from agir.lib.search import PrefixSearchQuery
from agir.lib.utils import front_url


class RegexExtractorValidator:
    pass


class CommunePageQueryset(models.QuerySet):
    def search(self, search_terms):
        vector = SearchVector(
            models.F("name"), config="simple_unaccented", weight="A"
        ) + SearchVector(
            models.F("code_departement"), config="simple_unaccented", weight="B"
        )
        query = PrefixSearchQuery(search_terms, config="simple_unaccented")

        return (
            self.annotate(search=vector)
            .filter(search=query)
            .annotate(rank=SearchRank(vector, query))
            .order_by("-rank")
        )


class CommunePage(TimeStampedModel, models.Model):
    objects = CommunePageQueryset.as_manager()

    published = models.BooleanField("Publiée", default=False, null=False)

    code = models.CharField("Code INSEE", max_length=5, editable=False)
    code_departement = models.CharField(
        "Code département", max_length=3, editable=False
    )
    coordinates = MultiPolygonField("Périmètre de la commune", geography=True)
    name = models.CharField("Nom de la commune", max_length=255)
    slug = models.SlugField("Slug")
    strategy = models.CharField("Stratégie", max_length=255, blank=True)
    first_name_1 = models.CharField(
        "Prénom chef⋅fe de file 1", max_length=255, blank=True
    )
    last_name_1 = models.CharField("Nom chef⋅fe de file 1", max_length=255, blank=True)
    first_name_2 = models.CharField(
        "Prénom chef⋅fe de file 2", max_length=255, blank=True
    )
    last_name_2 = models.CharField("Nom chef⋅fe de file 2", max_length=255, blank=True)
    twitter = TwitterProfileField(
        "Identifiant Twitter",
        blank=True,
        help_text="Indiquez l'identifiant ou l'URL du compte Twitter de la campagne.",
    )
    facebook = FacebookPageField(
        "Identifiant Facebook",
        max_length=255,
        blank=True,
        help_text="Indiquez l'identifiant ou l'URL de la page Facebook de la campagne",
    )

    website = models.URLField("Site web", max_length=255, blank=True)

    nom_mandataire = models.CharField(
        "Nom du manadataire financier", max_length=255, blank=True
    )
    adresse_mandataire = models.TextField(
        "Adresse complète du mandataire financier", blank=True
    )

    municipales2020_admins = models.ManyToManyField(
        "people.Person",
        verbose_name="Têtes de file pour les élections municipales de 2020",
        related_name="municipales2020_commune",
        blank=True,
    )

    def __str__(self):
        return "{} ({})".format(self.name, self.code_departement)

    def chief(self, number):
        first_name = getattr(self, "first_name_" + number)
        last_name = getattr(self, "last_name_" + number)
        if not any([first_name, last_name]):
            return ""

        if all([first_name, last_name]):
            return first_name + " " + last_name

        return first_name or last_name

    @property
    def chief_1(self):
        return self.chief("1")

    @property
    def chief_2(self):
        return self.chief("2")

    @property
    def chiefs(self):
        if not any([self.chief_1, self.chief_2]):
            return ""

        if all([self.chief_1, self.chief_2]):
            return self.chief_1 + " et " + self.chief_2

        return self.chief_1 or self.chief_2

    def get_absolute_url(self):
        return front_url(
            "view_commune",
            kwargs={"code_departement": self.code_departement, "slug": self.slug},
        )

    class Meta:
        constraints = (
            UniqueConstraint(fields=["code_departement", "slug"], name="dep_slug"),
        )
        verbose_name = "Page de commune"
        verbose_name_plural = "Pages de commune"
