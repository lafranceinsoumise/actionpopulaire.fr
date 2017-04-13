from django.db import models
from django.utils.translation import ugettext_lazy as _

from lib.models import (
    APIResource, AbstractLabel, NationBuilderResource, ContactMixin, LocationMixin
)


class Event(APIResource, LocationMixin, ContactMixin):
    """
    Model that represents an event
    """
    name = models.CharField(
        _("nom"),
        max_length=255,
        blank=False,
        help_text=_("Le nom du groupe de l'événement"),
    )

    description = models.TextField(
        _('description'),
        blank=True,
        help_text=_("Une description de l'événement, en MarkDown"),
    )

    nb_path = models.CharField(_('NationBuilder path'), max_length=255, blank=True)

    tags = models.ManyToManyField('EventTag', related_name='events', blank=True)

    start_time = models.DateTimeField(_('date et heure de début'), blank=False)
    end_time = models.DateTimeField(_('date et heure de fin'), blank=False)

    calendar = models.ForeignKey('Calendar', related_name='events', blank=False)

    class Meta:
        verbose_name = _('événement')
        verbose_name_plural = _('événements')

    def __str__(self):
        return self.name


class EventTag(AbstractLabel):
    class Meta:
        verbose_name = 'tag'


class Calendar(NationBuilderResource, AbstractLabel):
    class Meta:
        verbose_name = 'agenda'

