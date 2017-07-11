from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel

from lib.models import (
    BaseAPIResource, AbstractLabel, NationBuilderResource, ContactMixin, LocationMixin
)


class SupportGroup(BaseAPIResource, NationBuilderResource, LocationMixin, ContactMixin):
    """
    Model that represents a support group 
    """
    name = models.CharField(
        _("nom"),
        max_length=255,
        blank=False,
        help_text=_("Le nom du groupe d'appui"),
    )

    description = models.TextField(
        _('description'),
        blank=True,
        help_text=_("Une description du groupe d'appui, en MarkDown"),
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
            models.Index(fields=['nb_path'], name='nb_path_index'),
        )
        ordering = ('-created', )
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
        on_delete=models.CASCADE
    )

    supportgroup = models.ForeignKey(
        'SupportGroup',
        related_name='memberships',
        on_delete=models.CASCADE
    )

    is_referent = models.BooleanField(_('membre référent'), default=False)
    is_manager = models.BooleanField(_('gestionnaire'), default=False)

    class Meta:
        verbose_name = _('adhésion')
        verbose_name_plural = _('adhésions')
        unique_together = ('supportgroup', 'person')
        permissions = (
            ('view_membership', _('Peut afficher les adhésions')),
        )

    def __str__(self):
        return _('{person} --> {supportgroup},  (référent = {is_referent})').format(
            person=self.person, supportgroup=self.supportgroup, is_referent=self.is_referent
        )
