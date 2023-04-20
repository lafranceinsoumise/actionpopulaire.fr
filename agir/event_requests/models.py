from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
from django.core import validators
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Prefetch, Count, Subquery, OuterRef
from django.db.models.functions import Coalesce
from django.utils import formats, timezone
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django_countries.fields import CountryField
from dynamic_filenames import FilePattern

from agir.events.models import Event
from agir.events.models import Event, Calendar
from agir.lib.documents import (
    render_svg_template,
    rsvg_convert,
    RSVG_CONVERT_AVAILABLE_FORMATS,
    RSVG_CONVERT_AVAILABLE_FORMAT_CHOICES,
)
from agir.lib.form_fields import CustomJSONEncoder
from agir.lib.models import BaseAPIResource, SimpleLocationMixin, DescriptionField

ASSET_FILE_PATH = FilePattern(
    filename_pattern="{app_label}/{model_name}/{instance.id}/{name}_{uuid:.8base32}{ext}"
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
    target_format = models.CharField(
        "Format de destination",
        null=False,
        blank=False,
        max_length=10,
        default=RSVG_CONVERT_AVAILABLE_FORMATS[0],
        choices=RSVG_CONVERT_AVAILABLE_FORMAT_CHOICES,
        help_text="Le format dans lequel le visuel est destiné à être sauvegardé",
    )

    def __str__(self):
        return f"{self.name} [{str(self.id)[:8]}]"

    def render(self, data=None):
        return render_svg_template(self.file, data)

    class Meta:
        verbose_name = "Template de visuel"
        verbose_name_plural = "Templates de visuels"


class EventAssetQueryset(models.QuerySet):
    def public(self):
        return self.filter(published=True)

    def renderable(self):
        return self.filter(template_id__isnull=False, event_id__isnull=False)


class EventAssetManager(models.Manager.from_queryset(EventAssetQueryset)):
    def create(self, *args, render_after_creation=True, **kwargs):
        event_asset = super(EventAssetManager, self).create(*args, **kwargs)

        if render_after_creation and event_asset.renderable:
            event_asset.render()

        if not event_asset.name and event_asset.template:
            event_asset.name = event_asset.template.name
            event_asset.save()

        return event_asset


class EventAsset(BaseAPIResource):
    objects = EventAssetManager()

    class EventAssetRenderingException(Exception):
        pass

    published = models.BooleanField(
        "Publié",
        default=False,
        help_text="Le visuel a déjà été mis à disposition ou pas des organisateur·ices de l'événement",
    )
    name = models.CharField("Nom", null=False, blank=False, max_length=200)
    file = models.FileField(
        "Fichier",
        max_length=255,
        null=True,
        blank=True,
        upload_to=ASSET_FILE_PATH,
        validators=[validators.FileExtensionValidator(RSVG_CONVERT_AVAILABLE_FORMATS)],
    )
    template = models.ForeignKey(
        "event_requests.EventAssetTemplate",
        verbose_name="template",
        on_delete=models.SET_NULL,
        related_name="+",
        null=True,
        blank=True,
    )
    event = models.ForeignKey(
        "events.Event",
        verbose_name="événement",
        on_delete=models.SET_NULL,
        related_name="event_assets",
        related_query_name="event_asset",
        null=True,
        blank=True,
    )
    extra_data = models.JSONField(
        "Données supplémentaires",
        default=dict,
        blank=True,
        encoder=CustomJSONEncoder,
        help_text="Les données qui seront utilisées, en plus de celles de l'événement, pour générer le visuel",
    )

    def __str__(self):
        return f"{self.name} (événement #{self.event_id})"

    @property
    def renderable(self):
        return self.template_id and self.event_id

    def render(self):
        if not self.renderable:
            raise self.EventAssetRenderingException(
                "Ce visuel ne peut plus être généré car l'événement et/ou le template ont été supprimés"
            )
        rendered_svg = self.template.render(
            data={"event": self.event, **self.extra_data}
        )
        self.name = self.template.name
        self.file = rsvg_convert(
            rendered_svg,
            to_format=self.template.target_format,
            filename=slugify(self.name),
        )
        self.save()

    class Meta:
        verbose_name = "Visuel de l'événement"
        verbose_name_plural = "Visuels des événements"
        ordering = ("-published", "-created")
        indexes = (
            models.Index(fields=("-published", "-created"), name="ordering_index"),
        )
        constraints = (
            models.UniqueConstraint(
                fields=["event", "template"],
                name="unique_event_asset_for_event_and_template",
                condition=models.Q(template__isnull=False),
            ),
        )


class ModelWithCalendarManager(models.Manager):
    def create(self, **kwargs):
        from agir.event_requests.actions import create_calendar_for_object

        with transaction.atomic():
            obj = super().create(**kwargs)
            create_calendar_for_object(obj)
            return obj


class EventThemeTypeQueryset(models.QuerySet):
    def with_admin_prefetch(self):
        return self.select_related(
            "event_themes", "calendar", "event_subtype"
        ).prefetch_related("event_asset_templates")


class EventThemeTypeManager(
    ModelWithCalendarManager.from_queryset(EventThemeTypeQueryset)
):
    pass


class EventThemeTypeEventRequestValidationMode(models.TextChoices):
    SINGLE_EVENT_SPEAKER_REQUEST = (
        "S",
        "Validation automatique à la sélection d'un·e intervenant·e",
    )
    MULTIPLE_EVENT_SPEAKER_REQUESTS = (
        "M",
        "Validation manuelle après sélection des intervenant·es",
    )


class EventThemeType(models.Model):
    objects = EventThemeTypeManager()

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
    email_to = models.EmailField(
        verbose_name="destinataire des e-mails",
        max_length=255,
        blank=False,
        null=False,
        default=settings.EMAIL_SUPPORT,
        help_text="Cette adresse sera utilisé comme destinataire de tous les e-mails transactionnels "
        "pour ce type de thème d'événement",
    )
    email_from = models.EmailField(
        verbose_name="expéditeur des e-mails",
        max_length=255,
        blank=False,
        null=False,
        default=settings.EMAIL_SUPPORT,
        help_text="Cette adresse sera utilisé comme expéditeur de tous les e-mails transactionnels "
        "pour ce type de thème d'événement",
    )
    EventRequestValidationMode = EventThemeTypeEventRequestValidationMode
    event_request_validation_mode = models.CharField(
        verbose_name="mode de validation des demandes d'évenements",
        choices=EventThemeTypeEventRequestValidationMode.choices,
        default=EventThemeTypeEventRequestValidationMode.SINGLE_EVENT_SPEAKER_REQUEST,
        null=False,
        blank=False,
        max_length=1,
    )
    has_event_speaker_request_emails = models.BooleanField(
        verbose_name="demander leur disponibilité aux intervenant·es",
        default=True,
        blank=False,
        null=False,
        help_text="Cocher la case pour qu'un e-mail de demande de disponibilité soit envoyé automatiquement aux "
        "intervenant·es lorsqu'une demande est créé pour l'un de leurs thèmes. Ne pas cocher pour pouvoir "
        "renseigner leurs disponibilités directement via l'admin",
    )
    event_speaker_request_email_subject = models.CharField(
        verbose_name="objet de l'e-mail aux intervenant·es",
        max_length=255,
        blank=True,
        null=False,
        default="",
        help_text="Ce texte sera utilisé comme objet de l'e-mail envoyé aux intervenant·es pour demander de renseigner "
        "leur disponibilité.",
    )
    event_speaker_request_email_body = DescriptionField(
        verbose_name="texte de l'e-mail aux intervenant·es",
        blank=True,
        null=False,
        default="",
        allowed_tags=settings.ADMIN_ALLOWED_TAGS,
        help_text="Ce texte sera utilisé comme corps de l'e-mail envoyé aux intervenant·es pour demander de renseigner "
        "leur disponibilité.",
    )
    event_asset_templates = models.ManyToManyField(
        "event_requests.EventAssetTemplate",
        verbose_name="Templates de visuels",
        related_name="event_theme_types",
        related_query_name="event_theme_type",
        blank=True,
    )

    def __str__(self):
        return self.name

    def get_event_speaker_request_email_bindings(self):
        subject = self.event_speaker_request_email_subject
        if not subject:
            subject = f"Nouvelles demandes de {self.name.lower()} sur vos thèmes"
        body = self.event_speaker_request_email_body
        if not body:
            body = (
                f"<p>De nouvelles demandes de {self.name.lower()} sur l'un des thèmes pour lesquels vous "
                f"avez été indiqué comme intervenant·e ont été faites.</p>"
            )
        return {
            "email_from": self.email_from,
            "subject": subject,
            "body": mark_safe(body),
        }

    class Meta:
        verbose_name = "Type de thème d'événement"
        verbose_name_plural = "Types de thème d'évenement"


class EventThemeQuerySet(models.QuerySet):
    def with_admin_prefetch(self):
        return (
            self.select_related("event_theme_type", "calendar")
            .prefetch_related("event_speakers", "event_asset_templates")
            .annotate(event_speaker_count=Count("event_speaker", distinct=True))
        )


class EventThemeManager(ModelWithCalendarManager.from_queryset(EventThemeQuerySet)):
    pass


class EventTheme(BaseAPIResource):
    objects = EventThemeManager()

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
        verbose_name="Templates de visuels",
        related_name="event_themes",
        related_query_name="event_theme",
        blank=True,
    )

    speaker_event_creation_email_subject = models.CharField(
        verbose_name="objet de l'e-mail à l'intervenant·e",
        max_length=255,
        default="",
        blank=True,
        null=False,
        help_text="Ce texte sera utilisé comme objet de l'e-mail envoyé à l'intervenant·e "
        "sélectionné·e lors de la création d'un événement. Si vide, l'e-mail ne sera pas envoyé.",
    )
    speaker_event_creation_email_body = DescriptionField(
        verbose_name="texte de l'e-mail à l'intervenant·e",
        default="",
        blank=True,
        null=False,
        allowed_tags=settings.ADMIN_ALLOWED_TAGS,
        help_text="Ce texte sera utilisé comme corps de l'e-mail envoyé à l'intervenant·e "
        "sélectionné·e lors de la création d'un événement. Le lien vers la page de l'événement et les coordonnées"
        "de l'organisateur·ice seront automatiquement ajoutés à la fin du message.",
    )

    organizer_event_creation_email_subject = models.CharField(
        verbose_name="objet de l'e-mail à l'organisateur·ice",
        max_length=255,
        default="",
        blank=True,
        null=False,
        help_text="Ce texte sera utilisé comme objet de l'e-mail envoyé à l'organisateur·ice "
        "lors de la création d'un événement. Si vide, l'e-mail ne sera pas envoyé.",
    )
    organizer_event_creation_email_body = DescriptionField(
        verbose_name="texte de l'e-mail à l'organisateur·ice",
        default="",
        blank=True,
        null=False,
        allowed_tags=settings.ADMIN_ALLOWED_TAGS,
        help_text="Ce texte sera utilisé comme corps de l'e-mail envoyé à l'organisateur·ice "
        "lors de la création d'un événement. Le lien vers la page de l'événement et les coordonnées"
        "de l'intervenant·e seront automatiquement ajoutés à la fin du message.",
    )

    event_creation_notification_email_subject = models.CharField(
        verbose_name="objet de l'e-mail de notification de validation",
        max_length=255,
        default="",
        blank=True,
        null=False,
        help_text="Ce texte sera utilisé comme objet de l'e-mail de notification de validation "
        "lors de la création d'un événement. Si vide, l'e-mail ne sera pas envoyé.",
    )
    event_creation_notification_email_body = DescriptionField(
        verbose_name="texte de l'e-mail de notification de validation",
        default="",
        blank=True,
        null=False,
        allowed_tags=settings.ADMIN_ALLOWED_TAGS,
        help_text="Ce texte sera utilisé comme corps de l'e-mail de notification de validation "
        "lors de la création d'un événement. Le lien vers la page de l'événement et les coordonnées"
        "de l'organisateur·ice et de l'intervenant·e seront automatiquement ajoutés à la fin du message.",
    )

    unretained_speaker_event_creation_email_subject = models.CharField(
        verbose_name="objet de l'e-mail aux intervenant·es non retenu·es",
        max_length=255,
        default="",
        blank=True,
        null=False,
        help_text="Ce texte sera utilisé comme objet de l'e-mail envoyé aux intervenant·es disponibles mais "
        "non retenu·es lors de la création d'un événement. Si vide, l'e-mail ne sera pas envoyé.",
    )
    unretained_speaker_event_creation_email_body = DescriptionField(
        verbose_name="texte de l'e-mail aux intervenant·es non retenu·es",
        default="",
        blank=True,
        null=False,
        allowed_tags=settings.ADMIN_ALLOWED_TAGS,
        help_text="Ce texte sera utilisé comme corps de l'e-mail envoyé aux intervenant·es disponibles mais "
        "non retenu·es lors de la création d'un événement. Le lien vers la page de l'événement sera automatiquement "
        "ajouté à la fin du message.",
    )

    def __str__(self):
        return self.name

    def get_event_asset_templates(self):
        # Defaults to the event theme type event asset templates
        # if no asset exists for the particular event theme
        if not self.event_asset_templates.exists():
            return self.event_theme_type.event_asset_templates.all()
        return self.event_asset_templates.all()

    def get_speaker_event_creation_email_bindings(self):
        if not self.speaker_event_creation_email_subject:
            return None

        return {
            "email_from": self.event_theme_type.email_from,
            "subject": self.speaker_event_creation_email_subject,
            "body": mark_safe(self.speaker_event_creation_email_body),
        }

    def get_organizer_event_creation_email_bindings(self):
        if not self.organizer_event_creation_email_subject:
            return None

        return {
            "email_from": self.event_theme_type.email_from,
            "subject": self.organizer_event_creation_email_subject,
            "body": mark_safe(self.organizer_event_creation_email_body),
        }

    def get_event_creation_notification_email_bindings(self):
        if not self.event_creation_notification_email_subject:
            return None

        return {
            "email_to": self.event_theme_type.email_to,
            "email_from": self.event_theme_type.email_from,
            "subject": self.event_creation_notification_email_subject,
            "body": mark_safe(self.event_creation_notification_email_body),
        }

    def get_unretained_speaker_event_creation_email_bindings(self):
        if not self.unretained_speaker_event_creation_email_subject:
            return None

        return {
            "email_from": self.event_theme_type.email_from,
            "subject": self.unretained_speaker_event_creation_email_subject,
            "body": mark_safe(self.unretained_speaker_event_creation_email_body),
        }

    def get_event_creation_emails_bindings(self):
        return {
            "speaker": self.get_speaker_event_creation_email_bindings(),
            "organizer": self.get_organizer_event_creation_email_bindings(),
            "notification": self.get_event_creation_notification_email_bindings(),
            "unretained_speakers": self.get_unretained_speaker_event_creation_email_bindings(),
        }

    class Meta:
        verbose_name = "Thème d'événement"
        verbose_name_plural = "Thèmes d'évenement"


class EventSpeakerQuerySet(models.QuerySet):
    def with_admin_prefetch(self):
        event_themes = Prefetch(
            "event_themes",
            queryset=EventTheme.objects.select_related("event_theme_type").only(
                "id", "name", "event_theme_type__name"
            ),
        )
        return self.prefetch_related("events", event_themes).select_related("person")

    def with_email(self):
        from agir.people.models import PersonEmail

        return self.select_related("person").annotate(
            email=Coalesce(
                "person__public_email__address",
                Subquery(
                    PersonEmail.objects.filter(person_id=OuterRef("person_id"))
                    .order_by("_bounced", "_order")
                    .values("address")[:1]
                ),
            )
        )

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
            "events", event_requests, event_speaker_requests, event_themes
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
    description = models.CharField(
        verbose_name="description",
        max_length=255,
        blank=True,
        null=False,
        default="",
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
            queryset = self.events
        else:
            queryset = queryset.filter(event_speakers__id=self.id)
        return queryset.with_serializer_prefetch(self.person).listed().upcoming()

    def get_title(self):
        strg = f"{self.person.get_full_name().title()}"
        if self.description:
            strg += f" · {self.description.lower()}"
        return strg

    def __str__(self):
        strg = f"{self.person.get_full_name()}"
        if self.description:
            strg += f" · {self.description}"
        if self.available:
            strg += " (✔)"
        else:
            strg += " (✖)"
        return strg

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

    @property
    def is_pending(self):
        return self.status == self.Status.PENDING and self.event is None

    @property
    def has_manual_validation(self):
        return (
            self.is_pending
            and self.event_theme.event_theme_type.event_request_validation_mode
            == EventThemeType.EventRequestValidationMode.MULTIPLE_EVENT_SPEAKER_REQUESTS
            and self.event_speaker_requests.filter(accepted=True).exists()
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
        ordering = ("status", "-created")
        indexes = (
            models.Index(
                fields=(
                    "status",
                    "-created",
                ),
            ),
        )


class EventSpeakerRequestQueryset(models.QuerySet):
    def answered(self):
        return self.filter(available__isnull=False)

    def accepted(self):
        return self.filter(
            event_request__status=EventRequest.Status.DONE, accepted=True
        )

    def unretained(self):
        return self.filter(
            event_request__status=EventRequest.Status.DONE,
            accepted=False,
            available=True,
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
        help_text="L'intervenant·e est disponible pour cette date",
    )
    accepted = models.BooleanField(
        verbose_name="confirmé·e",
        default=False,
        help_text="L'intervenant·e a été validé·e pour cette demande et cette date",
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
        return self.event_request.is_pending

    @property
    def is_unacceptable(self):
        return self.accepted and self.is_answerable

    @property
    def is_acceptable(self):
        return (
            self.available
            and not self.accepted
            and self.is_answerable
            and not self.event_request.event_speaker_requests.exclude(
                datetime=self.datetime
            )
            .filter(accepted=True)
            .exists()
        )

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
