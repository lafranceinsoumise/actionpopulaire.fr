from django.conf import settings
from django.contrib.postgres.search import SearchVector, SearchRank
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_prometheus.models import ExportModelOperationsMixin

from agir.lib.models import (
    BaseAPIResource,
    AbstractLabel,
    ContactMixin,
    LocationMixin,
    ImageMixin,
    DescriptionMixin,
    BaseSubtype,
    TimeStampedModel,
    ExternalLinkMixin,
)
from agir.lib.search import PrefixSearchQuery

__all__ = [
    "SupportGroup",
    "SupportGroupTag",
    "SupportGroupSubtype",
    "Membership",
    "TransferOperation",
    "SupportGroupExternalLink",
]


class SupportGroupQuerySet(models.QuerySet):
    def active(self):
        return self.filter(published=True)

    def certified(self):
        return self.filter(subtypes__label__in=settings.CERTIFIED_GROUP_SUBTYPES)

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

    TYPE_CHOICES = (
        (TYPE_LOCAL_GROUP, "Groupe local"),
        (TYPE_THEMATIC, "Groupe thématique"),
        (TYPE_FUNCTIONAL, "Groupe fonctionnel"),
    )

    TYPE_PARAMETERS = {
        TYPE_LOCAL_GROUP: {"color": "#4a64ac", "icon_name": "users"},
        TYPE_THEMATIC: {"color": "#49b37d", "icon_name": "book"},
        TYPE_FUNCTIONAL: {"color": "#e14b35", "icon_name": "cog"},
    }

    TYPE_DESCRIPTION = {
        TYPE_LOCAL_GROUP: "Les groupes locaux réunissent les personnes sur la base d'un territoire réduit (quartier, "
        "village ou petite ville), ceux étudiants d'un même lieu d'étude, professionnels d'un même "
        "lieu de travail. Chacun·e ne peut animer qu'un seul groupe local, étudiant et "
        "professionnel.",
        TYPE_THEMATIC: "Les groupes thématiques réunissent celles et ceux qui souhaitent agir ensemble sur un thème "
        "donné en lien avec les livrets thématiques de l'Avenir en Commun.",
        TYPE_FUNCTIONAL: "Les groupes fonctionnels rassemblent les personnes d'une même zone s'organisant à plusieurs "
        "pour accomplir des fonctions précises (gestion d'un local, organisation des manifestation, "
        "etc.)",
    }

    TYPE_DISABLED_DESCRIPTION = {
        TYPE_LOCAL_GROUP: "✅ Vous animez déjà deux groupes locaux",
        TYPE_THEMATIC: "✅ Vous animez déjà deux groupes thématiques",
        TYPE_FUNCTIONAL: "✅ Vous animez déjà deux groupes fonctionnels",
    }

    MEMBERSHIP_LIMIT = 30

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

    tags = models.ManyToManyField("SupportGroupTag", related_name="groups", blank=True)

    members = models.ManyToManyField(
        "people.Person", related_name="supportgroups", through="Membership", blank=True
    )

    @property
    def managers(self):
        return [
            m.person
            for m in self.memberships.filter(
                membership_type__gte=Membership.MEMBERSHIP_TYPE_MANAGER
            )
        ]

    @property
    def referents(self):
        return [
            m.person
            for m in self.memberships.filter(
                membership_type__gte=Membership.MEMBERSHIP_TYPE_REFERENT
            )
        ]

    @property
    def events_count(self):
        from agir.events.models import Event

        return self.organized_events.filter(visibility=Event.VISIBILITY_PUBLIC).count()

    @property
    def members_count(self):
        return Membership.objects.filter(supportgroup=self).count()

    @property
    def active_members_count(self):
        return Membership.objects.filter(
            membership_type__gte=Membership.MEMBERSHIP_TYPE_MEMBER, supportgroup=self
        ).count()

    @property
    def is_full(self):
        return False
        # (Temporarily disabled)
        # return (
        #     self.type == self.TYPE_LOCAL_GROUP
        #     and self.active_members_count >= self.MEMBERSHIP_LIMIT
        # )

    @property
    def is_certified(self):
        return self.subtypes.filter(
            label__in=settings.CERTIFIED_GROUP_SUBTYPES
        ).exists()

    @property
    def is_2022_certified(self):
        return self.subtypes.filter(
            label__in=settings.CERTIFIED_2022_GROUP_SUBTYPES
            + settings.CERTIFIED_GROUP_SUBTYPES
        ).exists()

    @property
    def allow_external(self):
        return self.subtypes.filter(allow_external=True).exists()

    @property
    def external_help_text(self):
        subtype = self.subtypes.filter(allow_external=True).first()
        return subtype.external_help_text or ""

    class Meta:
        verbose_name = _("groupe d'action")
        verbose_name_plural = _("groupes d'action")
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
        return f"{self.description} / ({self.label})"

    class Meta:
        verbose_name = _("sous-type")


class Membership(ExportModelOperationsMixin("membership"), TimeStampedModel):
    """
    Model that represents the membership of a person in a support group

    This model also indicates if the person is referent for this support group
    """

    MEMBERSHIP_TYPE_FOLLOWER = 5
    MEMBERSHIP_TYPE_MEMBER = 10
    MEMBERSHIP_TYPE_MANAGER = 50
    MEMBERSHIP_TYPE_REFERENT = 100
    MEMBERSHIP_TYPE_CHOICES = (
        (MEMBERSHIP_TYPE_FOLLOWER, "Abonné⋅e du groupe"),
        (MEMBERSHIP_TYPE_MEMBER, "Membre actif du groupe"),
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
        default=MEMBERSHIP_TYPE_FOLLOWER,
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
        ordering = ["-membership_type"]

    def __str__(self):
        return _("{person} --> {supportgroup},  ({type})").format(
            person=self.person,
            supportgroup=self.supportgroup,
            type=self.get_membership_type_display(),
        )

    @property
    def is_active_member(self):
        return self.membership_type >= Membership.MEMBERSHIP_TYPE_MEMBER

    @property
    def is_referent(self):
        return self.membership_type >= Membership.MEMBERSHIP_TYPE_REFERENT

    @property
    def is_manager(self):
        return self.membership_type >= Membership.MEMBERSHIP_TYPE_MANAGER


class TransferOperation(models.Model):
    timestamp = models.DateTimeField(
        "Heure de l'opération", auto_now_add=True, editable=False
    )
    manager = models.ForeignKey("people.Person", on_delete=models.SET_NULL, null=True)

    former_group = models.ForeignKey(
        SupportGroup, on_delete=models.CASCADE, related_name="+", editable=False
    )
    new_group = models.ForeignKey(
        SupportGroup,
        on_delete=models.SET_NULL,
        related_name="+",
        null=True,
        editable=False,
    )

    members = models.ManyToManyField("people.Person", related_name="+", editable=False)

    class Meta:
        verbose_name = "Transfert de membres"
        verbose_name_plural = "Transferts de membres"
        ordering = ("timestamp", "former_group")


class SupportGroupExternalLink(ExternalLinkMixin):

    supportgroup = models.ForeignKey(
        SupportGroup,
        on_delete=models.CASCADE,
        related_name="links",
        related_query_name="link",
        null=False,
    )

    class Meta:
        verbose_name = "Lien ou réseau social de l’équipe"
        verbose_name_plural = "Liens et réseaux sociaux de l’équipe"
