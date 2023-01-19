from django.conf import settings
from django.contrib.gis.db import models
from django.db import transaction
from django_countries.fields import CountryField

from agir.lib.form_fields import CustomJSONEncoder
from agir.lib.models import BaseAPIResource, DescriptionField, SimpleLocationMixin


class EventThemeType(models.Model):
    name = models.CharField("nom", blank=False, null=False, max_length=255)
    event_subtype = models.ForeignKey(
        "events.EventSubtype",
        verbose_name="sous-type d'événement lié",
        on_delete=models.PROTECT,
        related_name="+",
        null=False,
        blank=False,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Type de thème d'événement"
        verbose_name_plural = "Types de thème d'évenement"


class EventTheme(BaseAPIResource):
    name = models.CharField("nom", blank=False, null=False, max_length=255)
    description = DescriptionField(
        verbose_name="description",
        blank=True,
        null=False,
        allowed_tags=settings.ADMIN_ALLOWED_TAGS,
    )
    event_theme_type = models.ForeignKey(
        "EventThemeType",
        verbose_name="type de thème d'événement",
        on_delete=models.CASCADE,
        related_name="event_themes",
        related_query_name="event_theme",
        null=False,
        blank=False,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Thème d'événement"
        verbose_name_plural = "Thèmes d'évenement"


class EventSpeaker(BaseAPIResource):
    person = models.OneToOneField(
        "people.Person",
        verbose_name="personne",
        on_delete=models.PROTECT,
        related_name="event_speaker",
        null=False,
        blank=False,
    )
    event_themes = models.ManyToManyField(
        "EventTheme",
        verbose_name="thèmes",
        related_name="event_speakers",
        related_query_name="event_speaker",
        blank=False,
    )
    available = models.BooleanField(
        "Disponible",
        default=True,
        help_text="Cette personne est disponible pour recevoir "
        "des demandes d'événement",
    )

    def __str__(self):
        return str(self.person)

    class Meta:
        verbose_name = "Intervenant·e"
        verbose_name_plural = "Intervenant·es"


class EventRequestDate(models.Model):
    date = models.DateField("Date", unique=True, null=False, blank=False)

    def __str__(self):
        return self.date.strftime("%d/%m/%Y")

    class Meta:
        verbose_name = "Date de demande d'événement"
        verbose_name_plural = "Dates de demande d'évenement"
        ordering = ("date",)


class EventRequestQueryset(models.QuerySet):
    def pending(self):
        return self.filter(status=EventRequest.Status.PENDING)


class EventRequestManager(models.Manager.from_queryset(EventRequestQueryset)):
    def create_for_dates(self, dates, *args, **kwargs):
        with transaction.atomic():
            event_request = self.model(**kwargs)
            for event_request_date in EventRequestDate.objects.bulk_create(
                (EventRequestDate(date=date) for date in dates), ignore_conflicts=True
            ):
                event_request.dates.add(event_request_date)
            event_request.save(using=self._db)

            return event_request


class EventRequestStatus(models.IntegerChoices):
    PENDING = 0, "Demande en cours"
    DONE = 1, "Demande traitée"
    CANCELLED = 2, "Demande annulée"


class EventRequest(BaseAPIResource):
    objects = EventRequestManager()

    Status = EventRequestStatus

    status = models.IntegerField(
        verbose_name="état de la demande",
        choices=EventRequestStatus.choices,
        blank=False,
        null=False,
        default=EventRequestStatus.PENDING,
    )
    dates = models.ManyToManyField(
        "EventRequestDate",
        verbose_name="dates possibles",
        related_name="+",
        blank=True,
    )
    event_theme = models.ForeignKey(
        "EventTheme",
        verbose_name="thème",
        on_delete=models.PROTECT,
        related_name="event_requests",
        related_query_name="event_request",
        null=False,
        blank=False,
    )
    location_zip = models.CharField(
        "code postal", max_length=20, null=False, blank=False
    )
    location_city = models.CharField("ville", max_length=100, null=False, blank=False)
    location_country = CountryField(
        "pays",
        blank_label="(sélectionner un pays)",
        default="FR",
        blank=True,
        null=False,
    )
    event_data = models.JSONField(
        "Paramètres de l'événement",
        default=dict,
        blank=True,
        encoder=CustomJSONEncoder,
        help_text="Les données qui seront utilisées pour créer l'événement au moment de la validation",
    )
    event = models.OneToOneField(
        "events.Event",
        verbose_name="événement",
        on_delete=models.SET_NULL,
        related_name="+",
        null=True,
        blank=True,
    )

    @property
    def date_list(self):
        return ",".join([str(date) for date in self.dates.all()])

    def __str__(self):
        return (
            f"{str(self.pk)[:8]} "
            f"/ {self.event_theme.name} "
            f"/ {self.location_zip} {self.location_city}"
        )

    class Meta:
        verbose_name = "Demande d'événement"
        verbose_name_plural = "Demandes d'évenement"


class EventSpeakerRequestQueryset(models.QuerySet):
    def answered(self):
        return self.filter(status__isnull=False)


class EventSpeakerRequest(BaseAPIResource):
    objects = models.Manager.from_queryset(EventRequestQueryset)

    available = models.BooleanField(
        verbose_name="disponible",
        null=True,
        default=None,
        help_text="L'intervenant·e est disponible ou non",
    )
    event_request = models.ForeignKey(
        "EventRequest",
        verbose_name="demande d'événement",
        on_delete=models.CASCADE,
        related_name="event_speaker_requests",
        related_query_name="event_speaker_request",
    )
    event_speaker = models.ForeignKey(
        "EventSpeaker",
        verbose_name="intervenant·e",
        on_delete=models.CASCADE,
        related_name="event_speaker_requests",
        related_query_name="event_speaker_request",
    )
    event_request_date = models.ForeignKey(
        "EventRequestDate",
        verbose_name="date",
        on_delete=models.PROTECT,
        related_name="+",
    )

    def __str__(self):
        return f"{self.event_speaker.person} / {self.event_request_date} / {self.event_request}"

    class Meta:
        verbose_name = "Demande de disponibilité d'intervenant·e"
        verbose_name_plural = "Demandes de disponibilité d'intervenant·e"
        ordering = ("event_request_date",)
        indexes = (
            models.Index(
                fields=("event_request_date",),
            ),
        )
        constraints = (
            models.UniqueConstraint(
                fields=["event_request", "event_speaker", "event_request_date"],
                name="unique_for_request_speaker_date",
            ),
        )
