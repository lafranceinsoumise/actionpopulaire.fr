from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from model_utils.models import TimeStampedModel

from lib.models import (
    BaseAPIResource, AbstractLabel, NationBuilderResource, ContactMixin, LocationMixin
)


class Event(BaseAPIResource, NationBuilderResource, LocationMixin, ContactMixin):
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

    attendees = models.ManyToManyField('people.Person', related_name='events', through='RSVP')

    class Meta:
        verbose_name = _('événement')
        verbose_name_plural = _('événements')
        ordering = ('start_time', 'end_time')

    def __str__(self):
        return self.name

    @property
    def participants(self):
        return self.rsvps.aggregate(participants=models.Sum(models.F('guests') + 1))['participants']


class EventTag(AbstractLabel):
    class Meta:
        verbose_name = 'tag'


class Calendar(NationBuilderResource, AbstractLabel):
    class Meta:
        verbose_name = 'agenda'


class RSVP(TimeStampedModel):
    """
    Model that represents a RSVP for one person for an event.
    
    An additional field indicates if the person is bringing any guests with her
    """
    person = models.ForeignKey('people.Person', related_name='rsvps', on_delete=models.CASCADE)
    event = models.ForeignKey('Event', related_name='rsvps', on_delete=models.CASCADE)
    guests = models.PositiveIntegerField(_("nombre d'invités supplémentaires"), default=0, null=False)

    class Meta:
        verbose_name = 'RSVP'
        verbose_name_plural = 'RSVP'
        unique_together = ('person', 'event',)

    def __str__(self):
        return _('{person} --> {event} ({guests} invités').format(
            person=self.person, event=self.event, guests=self.guests
        )
