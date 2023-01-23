from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
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


class EventSpeakerQuerySet(models.QuerySet):
    def available(self):
        return self.filter(available=True)


class EventSpeaker(BaseAPIResource):
    object = EventSpeakerQuerySet.as_manager()

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
        return f"{str(self.person.get_full_name())} ({'disponible' if self.available else 'indisponible'})"

    class Meta:
        verbose_name = "Intervenant·e"
        verbose_name_plural = "Intervenant·es"


class EventRequestQueryset(models.QuerySet):
    def pending(self):
        return self.filter(status=EventRequest.Status.PENDING)


class EventRequestStatus(models.IntegerChoices):
    PENDING = 0, "Demande en cours"
    DONE = 1, "Demande traitée"
    CANCELLED = 2, "Demande annulée"


class EventRequest(BaseAPIResource):
    objects = EventRequestQueryset.as_manager()

    Status = EventRequestStatus

    status = models.IntegerField(
        verbose_name="état de la demande",
        choices=EventRequestStatus.choices,
        blank=False,
        null=False,
        default=EventRequestStatus.PENDING,
    )
    datetimes = ArrayField(
        base_field=models.DateTimeField(),
        verbose_name="dates possibles",
        blank=False,
        null=False,
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
    comment = models.TextField("Commentaire", blank=True, null=False)

    @property
    def date_list(self):
        return ", ".join(
            [
                datetime.date().strftime("%d/%m/%Y")
                for datetime in sorted(self.datetimes)
            ]
        )

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

    def accepted(self):
        return self.filter(accepted=False)


class EventSpeakerRequest(BaseAPIResource):
    objects = models.Manager.from_queryset(EventRequestQueryset)

    available = models.BooleanField(
        verbose_name="disponible",
        null=True,
        default=None,
        help_text="L'intervenant·e est disponible ou non",
    )
    accepted = models.BooleanField(
        verbose_name="confirmé·e",
        default=False,
        help_text="L'intervenant·e a été confirmé·e ou pas pour cette demande",
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
    datetime = models.DateTimeField(verbose_name="date", null=False, blank=False)
    comment = models.TextField("Commentaire", blank=True, null=False)

    def __str__(self):
        return (
            f"{self.event_speaker.person} / {self.datetime.date} / {self.event_request}"
        )

    class Meta:
        verbose_name = "Demande de disponibilité d'intervenant·e"
        verbose_name_plural = "Demandes de disponibilité d'intervenant·e"
        ordering = ("datetime",)
        indexes = (
            models.Index(
                fields=("datetime",),
            ),
        )
        constraints = (
            models.UniqueConstraint(
                fields=["event_request", "event_speaker", "datetime"],
                name="unique_for_request_speaker_datetime",
            ),
        )
