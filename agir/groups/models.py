import hashlib
from urllib.parse import urljoin

import reversion
from django.conf import settings
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from django.contrib.postgres.search import SearchVector, SearchRank
from django.db import models
from django.db.models import Subquery, OuterRef, Count, Q, Exists, Max
from django.db.models.functions import Coalesce
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django_prometheus.models import ExportModelOperationsMixin

from agir.activity.models import Activity
from agir.carte.models import StaticMapImage
from agir.lib.admin.utils import admin_url
from agir.lib.form_fields import CustomJSONEncoder
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

from agir.lib.utils import front_url


class SupportGroupQuerySet(models.QuerySet):
    def active(self):
        return self.filter(published=True)

    def certified(self):
        return self.filter(certification_date__isnull=False)

    def uncertified(self):
        return self.filter(certification_date__isnull=True)

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

    def with_static_map_image(self):
        return self.annotate(
            static_map_image=Subquery(
                StaticMapImage.objects.filter(
                    center__dwithin=(
                        OuterRef("coordinates"),
                        StaticMapImage.UNIQUE_CENTER_MAX_DISTANCE,
                    ),
                ).values("image")[:1],
            )
        )

    def with_organized_event_count(self):
        from agir.events.models import Event

        return self.annotate(
            organized_event_count=Count(
                "organized_events",
                filter=Q(organized_events__visibility=Event.VISIBILITY_PUBLIC),
                distinct=True,
            )
        )

    def with_promo_code_tag_exists(self):
        return self.annotate(
            has_promo_codes=Exists(
                SupportGroupTag.objects.filter(
                    groups__id=OuterRef("id"), label=settings.PROMO_CODE_TAG
                )
            )
        )

    def with_membership_count(self):
        return self.annotate(
            membership_count=Count(
                "memberships",
                distinct=True,
                filter=Q(memberships__person__role__is_active=True),
            )
        ).annotate(
            active_membership_count=Count(
                "memberships",
                distinct=True,
                filter=Q(
                    memberships__person__role__is_active=True,
                    memberships__membership_type__gte=Membership.MEMBERSHIP_TYPE_MEMBER,
                ),
            )
        )

    def with_person_membership_type(self, person=None):
        return self.annotate(
            person_membership_type=Max(
                "memberships__membership_type", filter=Q(memberships__person=person)
            )
        )

    def with_serializer_prefetch(self, person=None):
        qs = (
            self.prefetch_related("memberships", "subtypes")
            .with_promo_code_tag_exists()
            .with_organized_event_count()
            .with_membership_count()
            .with_person_membership_type(person)
        )
        return qs

    def near(self, coordinates=None, radius=None):
        if not coordinates:
            return self

        if radius is None:
            from agir.people.models import Person

            radius = Person.DEFAULT_ACTION_RADIUS

        return (
            self.exclude(coordinates__isnull=True)
            .filter(coordinates__dwithin=(coordinates, D(km=radius)))
            .annotate(distance=Distance("coordinates", coordinates))
        )


class MembershipQuerySet(models.QuerySet):
    def active(self):
        return self.filter(supportgroup__published=True).exclude(
            person__role__isnull=False, person__role__is_active=False
        )

    def with_email(self):
        from agir.people.models import PersonEmail

        return self.annotate(
            email=Coalesce(
                "person__public_email__address",
                Subquery(
                    PersonEmail.objects.filter(person_id=OuterRef("person_id"))
                    .order_by("_bounced", "_order")
                    .values("address")[:1]
                ),
            )
        )

    def with_serializer_prefetch(self):
        return (
            self.select_related("person")
            .prefetch_related("subscription_set")
            .with_email()
        )


@reversion.register(for_concrete_model=True, follow=("subtypes", "links"))
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
    TYPE_BOUCLE_DEPARTEMENTALE = "D"

    TYPE_CHOICES = (
        (TYPE_LOCAL_GROUP, "Groupe local"),
        (TYPE_THEMATIC, "Groupe thématique"),
        (TYPE_FUNCTIONAL, "Groupe fonctionnel"),
        (TYPE_BOUCLE_DEPARTEMENTALE, "Boucle départementale"),
    )

    TYPE_PARAMETERS = {
        TYPE_LOCAL_GROUP: {"color": "#4a64ac", "icon_name": "users"},
        TYPE_THEMATIC: {"color": "#49b37d", "icon_name": "book"},
        TYPE_FUNCTIONAL: {"color": "#e14b35", "icon_name": "cog"},
        TYPE_BOUCLE_DEPARTEMENTALE: {"color": "#e4b363", "icon_name": "stroopwafel"},
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
        TYPE_BOUCLE_DEPARTEMENTALE: "Les boucles départementales assurent la coordination des groupes d'action au sein"
        "d'un département.",
    }

    TYPE_DISABLED_DESCRIPTION = {
        TYPE_LOCAL_GROUP: "✅ Vous animez déjà deux groupes locaux",
        TYPE_THEMATIC: "✅ Vous animez déjà deux groupes thématiques",
        TYPE_FUNCTIONAL: "✅ Vous animez déjà deux groupes fonctionnels",
        TYPE_BOUCLE_DEPARTEMENTALE: "✅ Il n'est pas possible de créer de boucle départementale vous-même",
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

    tags = models.ManyToManyField("SupportGroupTag", related_name="groups", blank=True)

    members = models.ManyToManyField(
        "people.Person", related_name="supportgroups", through="Membership", blank=True
    )

    published = models.BooleanField(
        _("publié"),
        default=True,
        blank=False,
        help_text=_("Le groupe est visible publiquement"),
    )

    open = models.BooleanField(
        _("ouvert"),
        default=True,
        blank=False,
        null=False,
        help_text=_("Le groupe accueilir de nouveaux membres ou abonné·es"),
    )

    editable = models.BooleanField(
        _("éditable"),
        default=True,
        blank=False,
        null=False,
        help_text=_(
            "Les informations du groupe peuvent être éditées par ses animateur·ices et gestionnaires"
        ),
    )

    is_private_messaging_enabled = models.BooleanField(
        _("messagerie privée activée"),
        default=True,
        blank=False,
        help_text=_("La messagerie privée est activée pour le groupe"),
    )

    certification_date = models.DateTimeField(
        verbose_name=_("date de certification"),
        default=None,
        null=True,
        blank=True,
        help_text=_(
            "La date à laquelle le groupe a été certifié, vide pour les groupes non certifiés"
        ),
    )

    @property
    def managers(self):
        return [
            m.person
            for m in self.memberships.filter(
                membership_type__gte=Membership.MEMBERSHIP_TYPE_MANAGER
            )
            .select_related("person")
            .with_email()
        ]

    @property
    def referents(self):
        return [
            m.person
            for m in self.memberships.filter(
                membership_type__gte=Membership.MEMBERSHIP_TYPE_REFERENT
            )
            .select_related("person")
            .with_email()
        ]

    @property
    def events_count(self):
        if hasattr(self, "organized_event_count"):
            return self.organized_event_count
        return self.organized_events.public().count()

    @property
    def members_count(self):
        if hasattr(self, "membership_count"):
            return self.membership_count
        return self.memberships.active().count()

    @property
    def active_members_count(self):
        if hasattr(self, "active_membership_count"):
            return self.active_membership_count
        return (
            self.memberships.active()
            .filter(membership_type__gte=Membership.MEMBERSHIP_TYPE_MEMBER)
            .count()
        )

    @property
    def is_full(self):
        return False
        # return (
        #     self.type == self.TYPE_LOCAL_GROUP
        #     and self.active_members_count >= self.MEMBERSHIP_LIMIT
        # )
        # (disabled until further notice)

    @property
    def is_certifiable(self):
        return len(self.referents) >= 2 and (
            self.type in settings.CERTIFIABLE_GROUP_TYPES
            or self.subtypes.filter(
                label__in=settings.CERTIFIABLE_GROUP_SUBTYPES
            ).exists()
        )

    @cached_property
    def is_certified(self):
        return self.certification_date is not None

    @cached_property
    def uncertifiable_warning_date(self):
        if self.certification_date is not None:
            warning = (
                self.notifications.filter(
                    type=Activity.TYPE_UNCERTIFIABLE_GROUP_WARNING,
                    supportgroup=self,
                )
                .filter(timestamp__gte=self.certification_date)
                .only("timestamp")
                .order_by("-timestamp")
                .first()
            )

            if warning is not None:
                return warning.timestamp

        return None

    @property
    def allow_external(self):
        return self.subtypes.filter(allow_external=True).exists()

    @property
    def external_help_text(self):
        subtype = self.subtypes.filter(allow_external=True).first()
        return subtype.external_help_text or ""

    def get_meta_image(self):
        if hasattr(self, "image") and self.image:
            return urljoin(settings.FRONT_DOMAIN, self.image.url)

        # Use content hash as cache key for the auto-generated meta image
        content = ":".join(
            (
                self.name,
                self.location_zip,
                self.location_city,
                str(self.coordinates),
                self.get_type_display(),
            )
        )
        content_hash = hashlib.sha1(content.encode("utf-8")).hexdigest()[:8]

        return front_url(
            "view_og_image_supportgroup",
            kwargs={"pk": self.pk, "cache_key": content_hash},
            absolute=True,
        )

    def front_url(self):
        return front_url("view_group", args=(self.pk,), absolute=True)

    def admin_url(self):
        return admin_url(
            "admin:groups_supportgroup_change", args=(self.pk,), absolute=True
        )

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


class SupportGroupSubtypeQuerySet(models.QuerySet):
    def active(self):
        return self.exclude(label__in=settings.CERTIFIED_GROUP_SUBTYPES)


@reversion.register()
class SupportGroupSubtype(BaseSubtype):
    TYPES_PARAMETERS = SupportGroup.TYPE_PARAMETERS

    objects = SupportGroupSubtypeQuerySet.as_manager()

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

    default_subscriptions_enabled = models.BooleanField(
        _("Ajout des notifications par défaut du groupe après création"),
        default=True,
        help_text=_(
            "J'accepte de recevoir les notifications par défaut de ce groupe. Je pourrai changer mes préferences de "
            "notifications à tout moment. "
        ),
    )

    personal_information_sharing_consent = models.BooleanField(
        _(
            "Consentement au partage des informations personnelles avec les animateur·ices et gestionnaires du groupe"
        ),
        null=True,
        help_text=_(
            "J'accepte de partager mes informations personnelles avec les animateur·ices et gestionnaires de ce groupe"
        ),
    )

    meta = models.JSONField(
        "Données supplémentaires",
        default=dict,
        blank=True,
        encoder=CustomJSONEncoder,
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

    @property
    def description(self):
        return self.meta.get("description", "")


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


@reversion.register(follow=("supportgroup",))
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
