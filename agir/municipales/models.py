from django.contrib.gis.db.models import MultiPolygonField
from django.contrib.postgres.fields import ArrayField
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

    code = models.CharField("Code INSEE", max_length=10, editable=False)
    code_departement = models.CharField(
        "Code département", max_length=3, editable=False
    )
    coordinates = MultiPolygonField("Périmètre de la commune", geography=True)
    name = models.CharField("Nom de la commune", max_length=255)
    slug = models.SlugField("Slug")
    strategy = models.CharField("Stratégie", max_length=255, blank=True)

    tete_liste = models.CharField(
        "Nom de la tête de liste",
        max_length=255,
        blank=True,
        help_text="Le nom de la tête de liste, tel qu'il s'affichera publiquement",
    )

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

    website = models.URLField(
        "Site web",
        max_length=255,
        blank=True,
        help_text="Indiquez l'URL du site web de la liste en entier (avec le http:// ou le https://)",
    )

    ordre_don = models.CharField(
        "Ordre des chèques",
        max_length=255,
        blank=True,
        help_text="Indiquez l'ordre auquel les chèques de dons doivent être adressés.",
    )

    adresse_don = models.TextField(
        "Adresse complète pour les dons",
        blank=True,
        help_text="Cette adresse sera affichée sur la page pour inciter les visiteurs à envoyer leurs dons par chèque.",
    )

    contact_email = models.EmailField(
        "Adresse email de contact",
        max_length=255,
        blank=True,
        help_text="Une adresse email publique qui peut être utilisée pour contacter votre campagne",
    )

    mandataire_email = models.EmailField(
        "Adresse email du mandataire financier",
        max_length=255,
        blank=True,
        help_text="Nous aurons sans doute besoin pendant et après la campagne de transmettre des documents"
        " légaux au mandataire financier. Indiquez-nous une adresse qui nous permettra de le⋅a contacter à"
        " ce moment.",
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

    def title_case(self):
        return "".join(c.title() for c in self.slug.split("-"))

    def snake_case(self):
        return "_".join(self.slug.split("-"))

    class Meta:
        constraints = (
            UniqueConstraint(fields=["code_departement", "slug"], name="dep_slug"),
        )
        verbose_name = "Page de commune"
        verbose_name_plural = "Pages de commune"


NUANCES_CHOICES = [
    ("LDVC", "Divers centre"),
    ("LDVG", "Divers gauche"),
    ("LEXG", "Extrême gauche"),
    ("LDIV", "Divers"),
    ("LDVD", "Divers droite"),
    ("LREM", "LREM"),
    ("LUG", "Union de la gauche"),
    ("LUD", "Union de la droite"),
    ("LRN", "Rassemblement national"),
    ("LECO", "Autre Ecologiste"),
    ("LSOC", "Socialiste"),
    ("LCOM", "Communiste"),
    ("LFI", "FI"),
    ("LVEC", "EELV"),
    ("LUDI", "UDI"),
    ("LLR", "Les Républicains"),
    ("LDLF", "Debout la France"),
    ("LEXD", "Extrême droite"),
    ("LRDG", "Parti radical de gauche"),
    ("LMDM", "Modem"),
    ("LUC", "Union du centre"),
    ("LREG", "Régionaliste"),
    ("LGJ", "Gilets Jaunes"),
]


class Liste(models.Model):
    SOUTIEN_PUBLIC = "P"
    SOUTIEN_PREF = "O"
    SOUTIEN_NON = "N"
    SOUTIEN_CHOICES = (
        (SOUTIEN_PUBLIC, "Soutien et participation de la FI"),
        (SOUTIEN_PREF, "Préférence de la FI sans soutien"),
        (SOUTIEN_NON, "Non soutenue"),
    )

    code = models.CharField(
        verbose_name="Code", max_length=20, unique=True, editable=False
    )
    nom = models.CharField(verbose_name="Nom de la liste", max_length=300)
    commune = models.ForeignKey(
        CommunePage,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="listes",
        related_query_name="liste",
    )

    nuance = models.CharField(
        verbose_name="Nuance politique", max_length=4, choices=NUANCES_CHOICES
    )

    candidats = ArrayField(
        verbose_name="Candidats", base_field=models.CharField(max_length=200)
    )

    soutien = models.CharField(
        verbose_name="Soutien ou participation de la FI",
        max_length=1,
        choices=SOUTIEN_CHOICES,
        default=SOUTIEN_NON,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="commune_soutenue_unique",
                fields=["commune"],
                condition=~models.Q(soutien="N"),
            )
        ]
        ordering = ("code",)
