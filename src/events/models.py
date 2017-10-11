from django.db import models
from django.utils import formats, timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify
from model_utils.models import TimeStampedModel

from stdimage.models import StdImageField
from stdimage.utils import UploadToAutoSlug

from lib.models import (
    BaseAPIResource, AbstractLabel, NationBuilderResource, ContactMixin, LocationMixin
)


EVENT_GRACE_PERIOD = timezone.timedelta(hours=12)


def published_event_only():
    """Returns a Q object expressing the condition "published events only" """
    return models.Q(published=True, end_time__gt=timezone.now() - EVENT_GRACE_PERIOD)


class PublishedEventManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(published=True, end_time__gt=timezone.now() - EVENT_GRACE_PERIOD)


class PublishedRSVPManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            event__published=True, event__end_time__gt=timezone.now() - EVENT_GRACE_PERIOD)


class Event(BaseAPIResource, NationBuilderResource, LocationMixin, ContactMixin):
    """
    Model that represents an event
    """
    objects = models.Manager()
    scheduled = PublishedEventManager()

    name = models.CharField(
        _("nom"),
        max_length=255,
        blank=False,
        help_text=_("Le nom de l'événement"),
    )

    description = models.TextField(
        _('description'),
        blank=True,
        help_text=_("Une description de l'événement, en MarkDown"),
    )

    allow_html = models.BooleanField(
        _("autoriser le HTML dans la description"),
        default=False,
    )

    image = StdImageField(
        _("bannière de l'événement"),
        upload_to=UploadToAutoSlug(populate_from="name", path="events/banners/"),
        variations={
            'thumbnail': (400, 250),
            'banner': (1200, 400),
        },
        null=True, blank=True
    )

    published = models.BooleanField(
        _('publié'),
        default=True,
        help_text=_('L\'évenement doit-il être visible publiquement.')
    )

    nb_path = models.CharField(_('NationBuilder path'), max_length=255, blank=True)

    tags = models.ManyToManyField('EventTag', related_name='events', blank=True)

    start_time = models.DateTimeField(_('date et heure de début'), blank=False)
    end_time = models.DateTimeField(_('date et heure de fin'), blank=False)

    calendar = models.ForeignKey('Calendar', related_name='events', blank=False, on_delete=models.PROTECT)

    attendees = models.ManyToManyField('people.Person', related_name='events', through='RSVP')

    organizers = models.ManyToManyField('people.Person', related_name='organized_events', through="OrganizerConfig")

    class Meta:
        verbose_name = _('événement')
        verbose_name_plural = _('événements')
        ordering = ('-start_time', '-end_time')
        permissions = (
            # DEPRECIATED: every_event was set up as a potential solution to Rest Framework django permissions
            # Permission class default behaviour of requiring both global permissions and object permissions before
            # allowing users. Was not used in the end.s
            ('every_event', _('Peut éditer tous les événements')),
            ('view_hidden_event', _('Peut voir les événements non publiés')),
        )
        indexes = (
            models.Index(fields=['start_time', 'end_time'], name='events_datetime_index'),
            models.Index(fields=['end_time'], name='events_end_time_index'),
            models.Index(fields=['nb_path'], name='events_nb_path_index'),
        )

    def __str__(self):
        return self.name

    @property
    def participants(self):
        try:
            return self._participants
        except AttributeError:
            return self.rsvps.aggregate(participants=models.Sum(models.F('guests') + 1))['participants']

    def get_display_date(self):
        tz = timezone.get_current_timezone()
        start_time = self.start_time.astimezone(tz)
        end_time = self.end_time.astimezone(tz)

        if start_time.date() == end_time.date():
            date = formats.date_format(start_time, 'DATE_FORMAT')
            return _("Le {date}, de {start_hour} à {end_hour}").format(
                date=date,
                start_hour=formats.time_format(start_time, 'TIME_FORMAT'),
                end_hour=formats.time_format(end_time, 'TIME_FORMAT')
            )

        return _("Du {start_date}, {start_time} au {end_date}, {end_time}").format(
            start_date=formats.date_format(start_time, 'DATE_FORMAT'),
            start_time=formats.date_format(start_time, 'TIME_FORMAT'),
            end_date=formats.date_format(end_time, 'DATE_FORMAT'),
            end_time=formats.date_format(end_time, 'TIME_FORMAT'),
        )


class EventTag(AbstractLabel):
    class Meta:
        verbose_name = 'tag'


class CalendarManager(models.Manager):
    def create_calendar(self, name, slug=None, **kwargs):
        if slug is None:
            slug = slugify(name)

        return super().create(
            name=name,
            slug=slug,
            **kwargs
        )


class Calendar(NationBuilderResource):
    objects = CalendarManager()

    name = models.CharField(_("titre"), max_length=255)
    slug = models.SlugField(_("slug"))

    user_contributed = models.BooleanField(_('Les utilisateurs peuvent ajouter des événements'), default=False)

    description = models.TextField(_('description'), blank=True, help_text=_("Saisissez une description (HTML accepté)"))

    image = StdImageField(
        _("bannière"),
        upload_to=UploadToAutoSlug("name", path="events/calendars/"),
        variations={
            'thumbnail': (400, 250),
            'banner': (1200, 400),
        },
        null=True, blank=True,
    )

    class Meta:
        verbose_name = 'agenda'

    def __str__(self):
        return self.name


class RSVP(TimeStampedModel):
    """
    Model that represents a RSVP for one person for an event.
    
    An additional field indicates if the person is bringing any guests with her
    """
    objects = models.Manager()
    current = PublishedRSVPManager()

    person = models.ForeignKey('people.Person', related_name='rsvps', on_delete=models.CASCADE, editable=False)
    event = models.ForeignKey('Event', related_name='rsvps', on_delete=models.CASCADE, editable=False)
    guests = models.PositiveIntegerField(_("nombre d'invités supplémentaires"), default=0, null=False)

    canceled = models.BooleanField(_('Annulé'), default=False)

    notifications_enabled = models.BooleanField(_('Recevoir les notifications'), default=True)

    class Meta:
        verbose_name = 'RSVP'
        verbose_name_plural = 'RSVP'
        unique_together = ('event', 'person',)
        permissions = (
            ('view_rsvp', _('Peut afficher les RSVPs')),
        )

    def __str__(self):
        return _('{person} --> {event} ({guests} invités').format(
            person=self.person, event=self.event, guests=self.guests
        )


class OrganizerConfig(models.Model):
    person = models.ForeignKey('people.Person', related_name='organizer_configs', on_delete=models.CASCADE, editable=False)
    event = models.ForeignKey('Event', related_name='organizer_configs', on_delete=models.CASCADE, editable=False)

    is_creator = models.BooleanField(_("Créateur de l'événement"), default=False)

    notifications_enabled = models.BooleanField(_('Recevoir les notifications'), default=True)
