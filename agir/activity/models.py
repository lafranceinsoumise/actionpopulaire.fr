import dynamic_filenames
from django.db import models
from django.utils import timezone
from stdimage import StdImageField
from stdimage.validators import MinSizeValidator

from agir.lib.models import TimeStampedModel, DescriptionField, BaseAPIResource
from agir.notifications.types import SubscriptionType

__all__ = ["Activity", "Announcement"]


class ActivityQuerySet(models.QuerySet):
    def displayed(self):
        return self.filter(type__in=SubscriptionType.DISPLAYED_TYPES)


class ActivityManager(models.Manager.from_queryset(ActivityQuerySet)):
    def bulk_create(self, instances, send_post_save_signal=False, **kwargs):
        activities = super().bulk_create(instances, **kwargs)
        if send_post_save_signal:
            for instance in instances:
                models.signals.post_save.send(
                    instance.__class__, instance=instance, created=True
                )
        return activities


class Activity(TimeStampedModel):

    STATUS_UNDISPLAYED = "U"
    STATUS_DISPLAYED = "S"
    STATUS_INTERACTED = "I"
    STATUS_CHOICES = (
        (STATUS_UNDISPLAYED, "Pas encore présentée au destinataire"),
        (STATUS_DISPLAYED, "Présentée au destinataire"),
        (STATUS_INTERACTED, "Le destinataire a interagi avec"),
    )  # attention : l'ordre croissant par niveau d'interaction est important

    objects = ActivityManager()

    timestamp = models.DateTimeField(
        verbose_name="Date de la notification", null=False, default=timezone.now
    )

    type = models.CharField(
        "Type", max_length=50, choices=SubscriptionType.TYPE_CHOICES
    )

    recipient = models.ForeignKey(
        "people.Person",
        on_delete=models.CASCADE,
        related_name="received_notifications",
        related_query_name="received_notification",
    )

    status = models.CharField(
        "Statut", max_length=1, choices=STATUS_CHOICES, default=STATUS_UNDISPLAYED
    )

    pushed = models.BooleanField(
        "Notification push envoyée", default=False, null=False,
    )

    event = models.ForeignKey(
        "events.Event",
        on_delete=models.CASCADE,
        related_name="notifications",
        related_query_name="notification",
        null=True,
    )

    supportgroup = models.ForeignKey(
        "groups.SupportGroup",
        on_delete=models.CASCADE,
        related_name="notifications",
        related_query_name="notification",
        null=True,
    )

    individual = models.ForeignKey(
        "people.Person", on_delete=models.CASCADE, related_name="+", null=True
    )

    announcement = models.ForeignKey(
        "Announcement",
        on_delete=models.CASCADE,
        related_name="activities",
        related_query_name="activity",
        null=True,
    )

    meta = models.JSONField("Autres données", blank=True, default=dict)

    def __str__(self):
        return f"« {self.get_type_display()} » pour {self.recipient} ({self.timestamp})"

    def __repr__(self):
        return f"Activity(timestamp={self.timestamp!r}, type={self.type!r}, recipient={self.recipient!r})"

    class Meta:
        verbose_name = "Notice d'activité"
        verbose_name_plural = "Notices d'activité"
        ordering = ("-timestamp",)
        indexes = (
            models.Index(
                fields=("recipient", "timestamp"), name="notifications_by_recipient"
            ),
        )
        constraints = [
            models.UniqueConstraint(
                fields=["recipient", "announcement"],
                condition=models.Q(type="announcement"),
                name="unique_for_recipient_and_announcement",
            ),
        ]


class AnnouncementQuerySet(models.QuerySet):
    def active(self):
        now = timezone.now()

        return self.filter(
            (models.Q(start_date__lt=now))
            & (models.Q(end_date__isnull=True) | models.Q(end_date__gt=now))
        )


class Announcement(BaseAPIResource):
    objects = AnnouncementQuerySet.as_manager()

    title = models.CharField(
        verbose_name="Titre de l'annonce",
        max_length=200,
        help_text="Ce texte sera utilisé comme titre de l'annonce",
        blank=False,
    )

    custom_display = models.SlugField(
        verbose_name="Affichage personnalisé",
        blank=True,
        help_text="Ce champ sert au pôle outils numériques",
    )

    link = models.URLField(verbose_name="Lien", blank=False)

    link_label = models.CharField(
        verbose_name="Libellé du lien",
        max_length=200,
        help_text="Ce texte sera utilisé comme texte du lien de l'annonce",
        blank=False,
        null=False,
        default="En savoir plus",
    )

    content = DescriptionField(verbose_name="Contenu", blank=False)

    image = StdImageField(
        verbose_name="Bannière",
        validators=[MinSizeValidator(255, 160)],
        variations={
            "desktop": {"width": 255, "height": 130, "crop": True},
            "mobile": {"width": 160, "height": 160, "crop": True},
            "activity": {"width": 548, "height": 241, "crop": True},
        },
        upload_to=dynamic_filenames.FilePattern(
            filename_pattern="activity/announcements/{uuid:.2base32}/{uuid:s}{ext}"
        ),
        null=True,
        blank=True,
    )

    start_date = models.DateTimeField(
        verbose_name="Date de début", default=timezone.now
    )
    end_date = models.DateTimeField(verbose_name="Date de fin", null=True, blank=True)

    segment = models.ForeignKey(
        to="mailing.Segment",
        on_delete=models.CASCADE,
        related_name="notifications",
        related_query_name="notification",
        null=True,
        blank=True,
        help_text=(
            "Segment des personnes auquel ce message sera montré (laisser vide pour montrer à tout le monde)"
        ),
    )

    priority = models.IntegerField(
        verbose_name="Priorité",
        default=0,
        help_text="Permet de modifier l'ordre d'affichage des annonces. Les valeurs plus élevées sont affichées avant."
        " Deux annonces de même priorité sont affichées dans l'ordre anti-chronologique (par date de début)",
    )

    def __str__(self):
        return f"« {self.title} »"

    class Meta:
        verbose_name = "Annonce"
        indexes = (
            models.Index(
                fields=("-start_date", "end_date"), name="announcement_date_index"
            ),
        )
        ordering = ("-start_date", "end_date")
