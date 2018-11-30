from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_prometheus.models import ExportModelOperationsMixin
from model_utils.models import TimeStampedModel

from agir.lib.models import (
    BaseAPIResource,
    AbstractLabel,
    NationBuilderResource,
    ContactMixin,
    LocationMixin,
    ImageMixin,
    DescriptionMixin,
    AbstractMapObjectLabel,
)


class SupportGroupQuerySet(models.QuerySet):
    def active(self):
        return self.filter(published=True)

    def certified(self):
        return self.filter(subtypes__label=settings.CERTIFIED_GROUP_SUBTYPE)


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
    TYPE_THEMATIC_BOOKLET = "B"
    TYPE_FUNCTIONAL = "F"
    TYPE_PROFESSIONAL = "P"

    TYPE_CHOICES = (
        (TYPE_LOCAL_GROUP, _("Groupe local")),
        (TYPE_THEMATIC_BOOKLET, _("Groupe thématique")),
        (TYPE_FUNCTIONAL, _("Groupe fonctionnel")),
        (TYPE_PROFESSIONAL, _("Groupe professionel")),
    )

    objects = SupportGroupQuerySet.as_manager()

    name = models.CharField(
        _("nom"), max_length=255, blank=False, help_text=_("Le nom du groupe d'action")
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

    tags = models.ManyToManyField("SupportGroupTag", related_name="events", blank=True)

    members = models.ManyToManyField(
        "people.Person", related_name="supportgroups", through="Membership", blank=True
    )

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


class SupportGroupTag(AbstractLabel):
    class Meta:
        verbose_name = _("tag")


class SupportGroupSubtype(AbstractMapObjectLabel):
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

    is_referent = models.BooleanField(_("animateur du groupe"), default=False)
    is_manager = models.BooleanField(_("autre gestionnaire du groupe"), default=False)

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
        return _("{person} --> {supportgroup},  (animateur = {is_referent})").format(
            person=self.person,
            supportgroup=self.supportgroup,
            is_referent=self.is_referent,
        )
