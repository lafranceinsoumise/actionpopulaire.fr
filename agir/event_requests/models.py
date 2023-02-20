import io

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
from django.core import validators
from django.core.exceptions import ValidationError
from django.core.files import File
from django.db import transaction
from django.db.models import Prefetch
from django.utils import formats, timezone
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django_countries.fields import CountryField
from dynamic_filenames import FilePattern

from agir.events.models import Event
from agir.events.models import Event, Calendar
from agir.lib.documents import render_svg_template, svg_to_pdf
from agir.lib.form_fields import CustomJSONEncoder
from agir.lib.models import BaseAPIResource, SimpleLocationMixin, DescriptionField

ASSET_FILE_PATH = FilePattern(
    filename_pattern="{app_label}/{model_name}/{instance.id}/{uuid:.8base32}{ext}"
)


class EventAssetTemplate(BaseAPIResource):
    name = models.CharField("Nom", null=False, blank=False, max_length=200)
    file = models.FileField(
        "Fichier",
        null=False,
        max_length=255,
        upload_to=ASSET_FILE_PATH,
        validators=[validators.FileExtensionValidator(["svg"])],
        help_text="Le fichier doit être au format SVG et contenir des variables correspondantes "
        "aux données d'un événement (au format: {{ nom_de_la_variable }})",
    )

    def __str__(self):
        return f"{self.name} [{str(self.id)[:8]}]"

    def render(self, data=None):
        return render_svg_template(self.file, data)

    class Meta:
        verbose_name = "Template de visuel"
        verbose_name_plural = "Templates de visuels"


class EventAssetManager(models.Manager):
    def create(self, *args, **kwargs):
        event_asset = super(EventAssetManager, self).create(*args, **kwargs)
        event_asset.render()
        return event_asset


class EventAsset(BaseAPIResource):
    objects = EventAssetManager()

    class EventAssetRenderingException(Exception):
        pass

    name = models.CharField(
        "Nom", null=False, blank=False, editable=False, max_length=200
    )
    file = models.FileField(
        "Fichier",
        null=False,
        editable=False,
        max_length=255,
        upload_to=ASSET_FILE_PATH,
        validators=[validators.FileExtensionValidator(["pdf"])],
    )
    template = models.ForeignKey(
        "event_requests.EventAssetTemplate",
        verbose_name="template",
        on_delete=models.SET_NULL,
        related_name="+",
        null=True,
        blank=False,
    )
    event = models.ForeignKey(
        "events.Event",
        verbose_name="événement",
        on_delete=models.SET_NULL,
        related_name="event_assets",
        related_query_name="event_asset",
        null=True,
        blank=False,
        editable=False,
    )
    extra_data = models.JSONField(
        "Données supplémentaires",
        default=dict,
        blank=True,
        encoder=CustomJSONEncoder,
        help_text="Les données qui seront utilisées, en plus de celles de l'événement, pour générer le visuel",
    )

    def __str__(self):
        if self.deprecated:
            return f"{self.name} (obsolète)"
        return f"{self.name} (événement #{self.event_id})"

    @property
    def deprecated(self):
        return self.template_id is None or self.event_id is None

    def render(self):
        if self.deprecated:
            raise self.EventAssetRenderingException(
                "Ce visuel est obsolète : l'événement et/ou le template ont été supprimés"
            )
        rendered_svg = self.template.render(
            data={"event": self.event, **self.extra_data}
        )
        self.name = self.template.name
        self.file = File(
            io.BytesIO(svg_to_pdf(rendered_svg)), name=f"{slugify(self.name)}.pdf"
        )
        self.save()

    class Meta:
        verbose_name = "Visuel de l'événement"
        verbose_name_plural = "Visuels des événements"
        constraints = (
            models.UniqueConstraint(
                fields=["event", "template"],
                name="unique_event_asset_for_event_and_template",
            ),
        )


class ModelWithCalendarManager(models.Manager):
    def create(self, **kwargs):
        from agir.event_requests.actions import create_calendar_for_object

        with transaction.atomic():
            obj = super().create(**kwargs)
            create_calendar_for_object(obj)
            return obj


class EventThemeType(models.Model):
    objects = ModelWithCalendarManager()

    name = models.CharField("nom", blank=False, null=False, max_length=255)
    event_subtype = models.ForeignKey(
        "events.EventSubtype",
        verbose_name="sous-type d'événement lié",
        on_delete=models.PROTECT,
        related_name="+",
        null=False,
        blank=False,
    )
    calendar = models.OneToOneField(
        "events.Calendar",
        on_delete=models.SET_NULL,
        verbose_name="Agenda",
        related_name="+",
        null=True,
        default=None,
        editable=False,
    )
    event_speaker_request_email_from = models.EmailField(
        verbose_name="expéditeur de l'e-mail aux intervenant·es",
        max_length=255,
        blank=False,
        null=False,
        default=settings.EMAIL_SUPPORT,
        help_text="Cette adresse sera utilisé comme expéditeur de l'e-mail envoyé aux intervenant·es pour demander de renseigner "
        "leur disponibilité.",
    )
    event_speaker_request_email_subject = models.CharField(
        verbose_name="objet de l'e-mail aux intervenant·es",
        max_length=255,
        blank=False,
        null=False,
        help_text="Ce texte sera utilisé comme objet de l'e-mail envoyé aux intervenant·es pour demander de renseigner "
        "leur disponibilité.",
    )
    event_speaker_request_email_body = DescriptionField(
        verbose_name="texte de l'e-mail aux intervenant·es",
        blank=False,
        null=False,
        allowed_tags=settings.ADMIN_ALLOWED_TAGS,
        help_text="Ce texte sera utilisé comme corps de l'e-mail envoyé aux intervenant·es pour demander de renseigner "
        "leur disponibilité.",
    )
    event_asset_templates = models.ManyToManyField(
        "event_requests.EventAssetTemplate",
        related_name="event_theme_types",
        related_query_name="event_theme_type",
        blank=True,
    )

    def __str__(self):
        return self.name

    def get_event_speaker_request_email_bindings(self):
        return {
            "email_from": self.event_speaker_request_email_from,
            "subject": self.event_speaker_request_email_subject,
            "body": mark_safe(self.event_speaker_request_email_body),
        }

    class Meta:
        verbose_name = "Type de thème d'événement"
        verbose_name_plural = "Types de thème d'évenement"


class EventTheme(BaseAPIResource):
    objects = ModelWithCalendarManager()

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

    calendar = models.OneToOneField(
        "events.Calendar",
        on_delete=models.SET_NULL,
        verbose_name="Agenda",
        related_name="+",
        null=True,
        default=None,
        editable=False,
    )

    event_asset_templates = models.ManyToManyField(
        "event_requests.EventAssetTemplate",
        related_name="event_themes",
        related_query_name="event_theme",
        blank=True,
    )

    def __str__(self):
        return self.name

    def get_event_asset_templates(self):
        # Defaults to the event theme type event asset templates
        # if no asset exists for the particular event theme
        if not self.event_asset_templates.exists():
            return self.event_theme_type.event_asset_templates.all()
        return self.event_asset_templates.all()

    class Meta:
        verbose_name = "Thème d'événement"
        verbose_name_plural = "Thèmes d'évenement"


class EventSpeakerQuerySet(models.QuerySet):
    def with_serializer_prefetch(self):
        event_requests = Prefetch(
            "event_requests",
            queryset=EventRequest.objects.distinct()
            .select_related("event_theme", "event_theme__event_theme_type")
            .only(
                "id",
                "status",
                "event_theme__id",
                "event_theme__name",
                "event_theme__event_theme_type__name",
                "location_zip",
                "location_city",
                "location_country",
                "event_id",
            ),
        )
        event_speaker_requests = Prefetch(
            "event_speaker_requests",
            queryset=EventSpeakerRequest.objects.select_related("event_request").only(
                "event_speaker_id",
                "id",
                "available",
                "accepted",
                "datetime",
                "comment",
                "event_request_id",
                "event_request__status",
            ),
        )
        event_themes = Prefetch(
            "event_themes",
            queryset=EventTheme.objects.select_related("event_theme_type").only(
                "id", "name", "event_theme_type__name"
            ),
        )
        return self.prefetch_related(
            event_requests, event_speaker_requests, event_themes
        )

    def available(self):
        return self.filter(available=True)


class EventSpeaker(BaseAPIResource):
    objects = EventSpeakerQuerySet.as_manager()

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
    event_requests = models.ManyToManyField(
        "EventRequest",
        through="EventSpeakerRequest",
    )

    def get_upcoming_events(self, queryset=None):
        if queryset is None:
            queryset = (
                Event.objects.with_serializer_prefetch(self.person).listed().upcoming()
            )
        return queryset.filter(
            id__in=list(
                self.event_speaker_requests.filter(
                    event_request__status=EventRequest.Status.DONE, accepted=True
                ).values_list("event_request__event_id", flat=True)
            )
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
        related_name="event_request",
        related_query_name="event_request",
        null=True,
        blank=True,
    )
    comment = models.TextField("Commentaire", blank=True, null=False)

    @property
    def simple_datetimes(self):
        tz = timezone.get_current_timezone()
        return [
            formats.localize_input(dt.astimezone(tz), "%Y-%m-%d %H:%M")
            for dt in self.datetimes
        ]

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
        return self.filter(available__isnull=False)

    def accepted(self):
        return self.filter(
            event_request__status=EventRequest.Status.DONE, accepted=True
        )


class EventSpeakerRequestManager(
    models.Manager.from_queryset(EventSpeakerRequestQueryset)
):
    def bulk_create(self, instances, send_post_save_signal=False, **kwargs):
        activities = super().bulk_create(instances, **kwargs)
        if send_post_save_signal:
            for instance in instances:
                models.signals.post_save.send(
                    instance.__class__, instance=instance, created=True
                )
        return activities


class EventSpeakerRequest(BaseAPIResource):
    objects = EventSpeakerRequestManager()

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

    @property
    def is_answerable(self):
        return self.event_request.status == EventRequest.Status.PENDING

    @property
    def simple_datetime(self):
        tz = timezone.get_current_timezone()
        return formats.localize_input(self.datetime.astimezone(tz), "%Y-%m-%d %H:%M")

    def clean(self):
        if self.datetime:
            datetime = self.simple_datetime
            event_request_datetimes = self.event_request.simple_datetimes
            if datetime not in event_request_datetimes:
                raise ValidationError(
                    f"La date choisie ({datetime}) ne fait pas partie des dates indiquées "
                    f"pour cette demande d'événement. Valeurs possibiles : {event_request_datetimes}"
                )

    def __str__(self):
        return f"{self.event_speaker.person} / {self.simple_datetime} / {self.event_request}"

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
