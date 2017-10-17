from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel

from lib.models import (
    BaseAPIResource, AbstractLabel, NationBuilderResource, ContactMixin, LocationMixin, WithImageMixin
)


class ActiveSupportGroupManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(published=True)


class SupportGroup(BaseAPIResource, NationBuilderResource, LocationMixin, WithImageMixin, ContactMixin):
    """
    Model that represents a support group 
    """
    TYPE_LOCAL_GROUP = "L"
    TYPE_THEMATIC_BOOKLET = "B"

    TYPE_CHOICES = (
        (TYPE_LOCAL_GROUP, _("Groupe local")),
        (TYPE_THEMATIC_BOOKLET, _("Livret thématique"))
    )

    objects = models.Manager()
    active = ActiveSupportGroupManager()

    name = models.CharField(
        _("nom"),
        max_length=255,
        blank=False,
        help_text=_("Le nom du groupe d'appui"),
    )

    type = models.CharField(
        _("type de groupe"),
        max_length=1,
        blank=False,
        default=TYPE_LOCAL_GROUP,
        choices=TYPE_CHOICES
    )

    description = models.TextField(
        _('description'),
        blank=True,
        help_text=_("Une description du groupe d'appui, en MarkDown"),
    )

    allow_html = models.BooleanField(
        _("autoriser le HTML dans la description"),
        default=False,
    )

    published = models.BooleanField(
        _('publié'),
        default=True,
        blank=False,
        help_text=_('Le groupe doit-il être visible publiquement.')
    )

    nb_path = models.CharField(_('NationBuilder path'), max_length=255, blank=True)

    tags = models.ManyToManyField('SupportGroupTag', related_name='events', blank=True)

    members = models.ManyToManyField('people.Person', related_name='supportgroups', through='Membership', blank=True)

    class Meta:
        verbose_name = _("groupe d'appui")
        verbose_name_plural = _("groupes d'appui")
        indexes = (
            models.Index(fields=['nb_path'], name='groups_nb_path_index'),
        )
        ordering = ('-created',)
        permissions = (
            ('view_hidden_supportgroup', _('Peut afficher les groupes non publiés')),
        )

    def __str__(self):
        return self.name


class SupportGroupTag(AbstractLabel):
    class Meta:
        verbose_name = _('tag')


class Membership(TimeStampedModel):
    """
    Model that represents the membership of a person in a support group
    
    This model also indicates if the person is referent for this support group
    """
    person = models.ForeignKey(
        'people.Person',
        related_name='memberships',
        on_delete=models.CASCADE,
        editable=False,
    )

    supportgroup = models.ForeignKey(
        'SupportGroup',
        related_name='memberships',
        on_delete=models.CASCADE,
        editable=False,
    )

    is_referent = models.BooleanField(_('animateur du groupe'), default=False)
    is_manager = models.BooleanField(_('autre gestionnaire du groupe'), default=False)

    notifications_enabled = models.BooleanField(
        _('Recevoir les notifications de ce groupe'), default=True,
        help_text=_("Je recevrai des messages en cas de modification du groupe.")
    )

    class Meta:
        verbose_name = _('adhésion')
        verbose_name_plural = _('adhésions')
        unique_together = ('supportgroup', 'person')
        permissions = (
            ('view_membership', _('Peut afficher les adhésions')),
        )

    def __str__(self):
        return _('{person} --> {supportgroup},  (animateur = {is_referent})').format(
            person=self.person, supportgroup=self.supportgroup, is_referent=self.is_referent
        )
