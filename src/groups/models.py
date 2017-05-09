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

    nb_path = models.CharField(_('NationBuilder path'), max_length=255, blank=True)

    tags = models.ManyToManyField('SupportGroupTag', related_name='events', blank=True)

    members = models.ManyToManyField('people.Person', related_name='support_groups', through='Membership', blank=True)

    class Meta:
        verbose_name = _("groupe d'appui")
        verbose_name_plural = _("groupes d'appui")
        indexes = (
            models.Index(fields=['nb_path'], name='nb_path_index'),
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
    person = models.ForeignKey('people.Person', related_name='memberships', on_delete=models.CASCADE)
    support_group = models.ForeignKey('SupportGroup', related_name='memberships', on_delete=models.CASCADE)
    is_referent = models.BooleanField(_('membre référent'), default=False)

    class Meta:
        verbose_name = _('adhésion')
        verbose_name_plural = _('adhésions')
        unique_together = ('person', 'support_group',)

    def __str__(self):
        return _('{person} --> {support_group},  (référent = {is_referent})').format(
            person=self.person, support_group=self.support_group, is_referent=self.is_referent
        )
