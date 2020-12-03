from django.conf import settings
from django.contrib.postgres.search import SearchVector, SearchRank
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_prometheus.models import ExportModelOperationsMixin

from agir.lib.models import (
    BaseAPIResource,
    AbstractLabel,
    NationBuilderResource,
    ContactMixin,
    LocationMixin,
    ImageMixin,
    DescriptionMixin,
    BaseSubtype,
    TimeStampedModel,
)
from agir.lib.search import PrefixSearchQuery


class SupportGroupQuerySet(models.QuerySet):
    def active(self):
        return self.filter(published=True)

    def certified(self):
        return self.filter(subtypes__label__in=settings.CERTIFIED_GROUP_SUBTYPES)

    def is_2022(self):
        return self.filter(type=SupportGroup.TYPE_2022)

    def search(self, query):
        vector = (
            SearchVector(models.F("name"), config="french_unaccented", weight="A")
            + SearchVector(
                models.F("location_city"), config="french_unaccented", weight="B"
            )
            + SearchVector(
                models.F("location_zip"), config="french_unaccented", weight="B"
            )
            + SearchVector(
                models.F("description"), config="french_unaccented", weight="C"
            )
        )
        query = PrefixSearchQuery(query, config="french_unaccented")

        return (
            self.annotate(search=vector)
            .filter(search=query)
            .annotate(rank=SearchRank(vector, query))
            .order_by("-rank")
        )


class MembershipQuerySet(models.QuerySet):
    def active(self):
        return self.filter(supportgroup__published=True)


class SupportGroup(
    ExportModelOperationsMixin("support_group"),
    BaseAPIResource,
    NationBuilderResource,
    LocationMixin,
    ImageMixin,
    DescriptionMixin,
    ContactMixin,
):
    """
    Model that represents a support group
    """

    TYPE_LOCAL_GROUP = "L"
    TYPE_THEMATIC = "B"
    TYPE_FUNCTIONAL = "F"
    TYPE_PROFESSIONAL = "P"
    TYPE_2022 = "2"

    TYPE_CHOICES = (
        (TYPE_LOCAL_GROUP, "Groupe local"),
        (TYPE_THEMATIC, "Groupe thématique"),
        (TYPE_FUNCTIONAL, "Groupe fonctionnel"),
        (TYPE_PROFESSIONAL, "Groupe professionel"),
        (TYPE_2022, "Groupe de soutien « Nous Sommes Pour ! »"),
    )

    TYPE_PARAMETERS = {
        TYPE_LOCAL_GROUP: {"color": "#4a64ac", "icon_name": "users"},
        TYPE_THEMATIC: {"color": "#49b37d", "icon_name": "book"},
        TYPE_FUNCTIONAL: {"color": "#e14b35", "icon_name": "cog"},
        TYPE_PROFESSIONAL: {"color": "#f4981e", "icon_name": "industry"},
        TYPE_2022: {"color": "#571aff", "icon_name": "users"},
    }

    TYPE_DESCRIPTION = {
        TYPE_LOCAL_GROUP: "Les groupes d’action géographiques de la France insoumise sont constitués sur la base d’un"
        " territoire réduit (quartier, villages ou petites villes, cantons). Chaque insoumis⋅e peut assurer"
        " l’animation d’un seul groupe d’action géographique.",
        TYPE_THEMATIC: "Les groupes d’action thématiques réunissent des insoumis⋅es qui"
        " souhaitent agir de concert sur un thème donné en lien avec les livrets"
        " thématiques correspondant.",
        TYPE_FUNCTIONAL: "Les groupes d’action fonctionnels remplissent"
        " des fonctions précises (formations, organisation"
        " des apparitions publiques, rédaction de tracts, chorale insoumise,"
        " journaux locaux, auto-organisation, etc…).",
        TYPE_PROFESSIONAL: "Les groupes d’action professionnels rassemblent des insoumis⋅es qui"
        " souhaitent agir au sein de leur entreprise ou de leur lieu d’étude.",
        TYPE_2022: "Les groupes de soutien « Nous Sommes Pour ! » peuvent être rejoints par toutes les personnes "
        "ayant parainné la candidature de Jean-Luc Mélenchon.",
    }

    objects = SupportGroupQuerySet.as_manager()

    name = models.CharField(
        _("nom"), max_length=255, blank=False, help_text=_("Le nom du groupe")
    )

    type = models.CharField(
        _("type de groupe"),
        max_length=1,
        blank=False,
        default=TYPE_LOCAL_GROUP,
        choices=TYPE_CHOICES,
    )

    subtypes = models.ManyToManyField(
        "SupportGroupSubtype", related_name="supportgroups", blank=True
    )

    published = models.BooleanField(
        _("publié"),
        default=True,
        blank=False,
        help_text=_("Le groupe doit-il être visible publiquement."),
    )

    nb_path = models.CharField(_("NationBuilder path"), max_length=255, blank=True)

    tags = models.ManyToManyField("SupportGroupTag", related_name="groups", blank=True)

    members = models.ManyToManyField(
        "people.Person", related_name="supportgroups", through="Membership", blank=True
    )

    @property
    def events_count(self):
        from agir.events.models import Event

        return self.organized_events.filter(visibility=Event.VISIBILITY_PUBLIC).count()

    @property
    def members_count(self):
        return Membership.objects.filter(supportgroup=self).count()

    @property
    def is_certified(self):
        return self.subtypes.filter(
            label__in=settings.CERTIFIED_GROUP_SUBTYPES
        ).exists()

    @property
    def allow_external(self):
        return self.subtypes.filter(allow_external=True).exists()

    @property
    def external_help_text(self):
        subtype = self.subtypes.filter(allow_external=True).first()
        return subtype.external_help_text or ""

    @property
    def is_2022(self):
        return self.type == self.TYPE_2022

    class Meta:
        verbose_name = _("groupe d'action")
        verbose_name_plural = _("groupes d'action")
        indexes = (models.Index(fields=["nb_path"], name="groups_nb_path_index"),)
        ordering = ("-created",)
        permissions = (
            ("view_hidden_supportgroup", _("Peut afficher les groupes non publiés")),
        )

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"{self.__class__.__name__}(id={str(self.pk)!r}, name={self.name!r})"


class SupportGroupTag(AbstractLabel):
    class Meta:
        verbose_name = _("tag")


class SupportGroupSubtype(BaseSubtype):
    TYPES_PARAMETERS = SupportGroup.TYPE_PARAMETERS
    type = models.CharField(
        _("type de groupe"),
        max_length=1,
        blank=False,
        choices=SupportGroup.TYPE_CHOICES,
    )

    def __str__(self):
        return self.description

    class Meta:
        verbose_name = _("sous-type")


class Membership(ExportModelOperationsMixin("membership"), TimeStampedModel):
    """
    Model that represents the membership of a person in a support group

    This model also indicates if the person is referent for this support group
    """

    MEMBERSHIP_TYPE_MEMBER = 10
    MEMBERSHIP_TYPE_MANAGER = 50
    MEMBERSHIP_TYPE_REFERENT = 100
    MEMBERSHIP_TYPE_CHOICES = (
        (MEMBERSHIP_TYPE_MEMBER, "Membre du groupe"),
        (MEMBERSHIP_TYPE_MANAGER, "Membre gestionnaire"),
        (MEMBERSHIP_TYPE_REFERENT, "Animateur⋅rice"),
    )

    objects = MembershipQuerySet.as_manager()

    person = models.ForeignKey(
        "people.Person",
        related_name="memberships",
        on_delete=models.CASCADE,
        editable=False,
    )

    supportgroup = models.ForeignKey(
        "SupportGroup",
        related_name="memberships",
        on_delete=models.CASCADE,
        editable=False,
    )

    membership_type = models.IntegerField(
        _("Statut dans le groupe"),
        choices=MEMBERSHIP_TYPE_CHOICES,
        default=MEMBERSHIP_TYPE_MEMBER,
    )

    notifications_enabled = models.BooleanField(
        _("Recevoir les notifications de ce groupe"),
        default=True,
        help_text=_("Je recevrai des messages en cas de modification du groupe."),
    )

    class Meta:
        verbose_name = _("adhésion")
        verbose_name_plural = _("adhésions")
        unique_together = ("supportgroup", "person")

    def __str__(self):
        return _("{person} --> {supportgroup},  ({type})").format(
            person=self.person,
            supportgroup=self.supportgroup,
            type=self.get_membership_type_display(),
        )

    @property
    def is_referent(self):
        return self.membership_type >= Membership.MEMBERSHIP_TYPE_REFERENT

    @property
    def is_manager(self):
        return self.membership_type >= Membership.MEMBERSHIP_TYPE_MANAGER
