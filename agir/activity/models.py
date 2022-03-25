import dynamic_filenames
from django.db import models
from django.utils import timezone
from stdimage import StdImageField
from stdimage.validators import MinSizeValidator

from agir.lib.models import TimeStampedModel, DescriptionField, BaseAPIResource

#

__all__ = ["Activity", "Announcement"]


class ActivityQuerySet(models.QuerySet):
    def displayed(self):
        return self.filter(type__in=Activity.DISPLAYED_TYPES)


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

    TYPE_REFERRAL = "referral-accepted"

    # PERSON/EVENT TYPES
    TYPE_NEW_ATTENDEE = "new-attendee"
    TYPE_NEW_GROUP_ATTENDEE = "new-group-attendee"
    TYPE_EVENT_UPDATE = "event-update"
    TYPE_CANCELLED_EVENT = "cancelled-event"
    TYPE_WAITING_LOCATION_EVENT = "waiting-location-event"
    TYPE_WAITING_LOCATION_GROUP = "waiting-location-group"
    TYPE_EVENT_SUGGESTION = "event-suggestion"
    TYPE_ANNOUNCEMENT = "announcement"
    TYPE_REMINDER_DOCS_EVENT_EVE = "reminder-docs-event-eve"
    TYPE_REMINDER_DOCS_EVENT_NEXTDAY = "reminder-docs-event-nextday"
    TYPE_REMINDER_REPORT_FORM_FOR_EVENT = "reminder-report-form-for-event"
    TYPE_REMINDER_UPCOMING_EVENT_START = "reminder-upcoming-event-start"

    # GROUP TYPES
    TYPE_NEW_REPORT = "new-report"
    TYPE_NEW_EVENT_MYGROUPS = "new-event-mygroups"
    TYPE_NEW_EVENT_PARTICIPATION_MYGROUPS = "new-event-participation-mygroups"
    TYPE_GROUP_INVITATION = "group-invitation"
    TYPE_NEW_FOLLOWER = "new-follower"
    TYPE_NEW_MEMBER = "new-member"
    TYPE_MEMBER_STATUS_CHANGED = "member-status-changed"
    TYPE_GROUP_MEMBERSHIP_LIMIT_REMINDER = "group-membership-limit-reminder"
    TYPE_GROUP_INFO_UPDATE = "group-info-update"
    TYPE_NEW_MESSAGE = "new-message"
    TYPE_NEW_COMMENT = "new-comment"
    TYPE_NEW_COMMENT_RESTRICTED = "new-comment-restricted"
    TYPE_GROUP_CREATION_CONFIRMATION = "group-creation-confirmation"
    TYPE_ACCEPTED_INVITATION_MEMBER = "accepted-invitation-member"
    TYPE_TRANSFERRED_GROUP_MEMBER = "transferred-group-member"
    TYPE_NEW_MEMBERS_THROUGH_TRANSFER = "new-members-through-transfer"

    # TODO
    TYPE_GROUP_COORGANIZATION_INFO = "group-coorganization-info"
    TYPE_GROUP_COORGANIZATION_INVITE = "group-coorganization-invite"
    TYPE_GROUP_COORGANIZATION_ACCEPTED = "group-coorganization-accepted"
    TYPE_GROUP_COORGANIZATION_ACCEPTED_FROM = "group-coorganization-accepted-from"
    TYPE_GROUP_COORGANIZATION_ACCEPTED_TO = "group-coorganization-accepted-to"
    TYPE_WAITING_PAYMENT = "waiting-payment"

    DISPLAYED_TYPES = (
        TYPE_NEW_EVENT_PARTICIPATION_MYGROUPS,
        TYPE_GROUP_INVITATION,
        TYPE_NEW_FOLLOWER,
        TYPE_NEW_MEMBER,
        TYPE_MEMBER_STATUS_CHANGED,
        TYPE_GROUP_MEMBERSHIP_LIMIT_REMINDER,
        TYPE_GROUP_INFO_UPDATE,
        TYPE_NEW_ATTENDEE,
        TYPE_NEW_GROUP_ATTENDEE,
        TYPE_EVENT_UPDATE,
        TYPE_NEW_EVENT_MYGROUPS,
        TYPE_NEW_REPORT,
        TYPE_CANCELLED_EVENT,
        TYPE_REFERRAL,
        TYPE_GROUP_COORGANIZATION_INFO,
        TYPE_ACCEPTED_INVITATION_MEMBER,
        TYPE_WAITING_LOCATION_EVENT,
        TYPE_GROUP_COORGANIZATION_INVITE,
        TYPE_GROUP_COORGANIZATION_ACCEPTED,
        TYPE_GROUP_COORGANIZATION_ACCEPTED_FROM,
        TYPE_GROUP_COORGANIZATION_ACCEPTED_TO,
        TYPE_WAITING_LOCATION_GROUP,
        TYPE_WAITING_PAYMENT,
        TYPE_GROUP_CREATION_CONFIRMATION,
        TYPE_TRANSFERRED_GROUP_MEMBER,
        TYPE_NEW_MEMBERS_THROUGH_TRANSFER,
        TYPE_EVENT_SUGGESTION,
        TYPE_ANNOUNCEMENT,
        # Old required action types :
        TYPE_WAITING_PAYMENT,
    )

    TYPE_CHOICES = (
        (TYPE_WAITING_PAYMENT, "Paiement en attente"),
        (TYPE_NEW_EVENT_PARTICIPATION_MYGROUPS, "Le groupe participe à un événement"),
        (TYPE_GROUP_INVITATION, "Invitation à un groupe"),
        (TYPE_NEW_FOLLOWER, "Nouveau·lle abonné·e dans le groupe"),
        (TYPE_NEW_MEMBER, "Nouveau membre dans le groupe"),
        (
            TYPE_MEMBER_STATUS_CHANGED,
            "Un membre actif du groupe a été passé au statut abonné·e",
        ),
        (
            TYPE_GROUP_MEMBERSHIP_LIMIT_REMINDER,
            "Les membres du groupes sont de plus en plus nombreux",
        ),
        (TYPE_NEW_MESSAGE, "Nouveau message dans un de vos groupes"),
        (TYPE_NEW_COMMENT, "Nouveau commentaire dans un de vos groupes"),
        (
            TYPE_NEW_COMMENT_RESTRICTED,
            "Nouveau commentaire dans une de vos discussions",
        ),
        (TYPE_WAITING_LOCATION_GROUP, "Préciser la localisation du groupe"),
        (TYPE_WAITING_LOCATION_EVENT, "Préciser la localisation d'un événement"),
        (
            TYPE_GROUP_COORGANIZATION_INVITE,
            "Invitation à coorganiser un événement reçue",
        ),
        (
            TYPE_GROUP_COORGANIZATION_ACCEPTED,
            "Invitation à coorganiser un événement acceptée",
        ),
        (
            TYPE_GROUP_COORGANIZATION_ACCEPTED_FROM,
            "Invitation de leur groupe à coorganiser mon événement acceptée",
        ),
        (
            TYPE_GROUP_COORGANIZATION_ACCEPTED_TO,
            "Invitation de mon groupe à coorganiser leur événement acceptée",
        ),
        (TYPE_GROUP_INFO_UPDATE, "Mise à jour des informations du groupe"),
        (TYPE_ACCEPTED_INVITATION_MEMBER, "Invitation à rejoindre un groupe acceptée"),
        (TYPE_NEW_ATTENDEE, "Un nouveau participant à votre événement"),
        (TYPE_NEW_GROUP_ATTENDEE, "Un nouveau groupe participant à votre événement"),
        (TYPE_EVENT_UPDATE, "Mise à jour d'un événement"),
        (TYPE_NEW_EVENT_MYGROUPS, "Votre groupe organise un événement"),
        (TYPE_NEW_REPORT, "Nouveau compte-rendu d'événement"),
        (TYPE_CANCELLED_EVENT, "Événement annulé"),
        (TYPE_REFERRAL, "Personne parrainée"),
        (TYPE_ANNOUNCEMENT, "Associée à une annonce"),
        (
            TYPE_TRANSFERRED_GROUP_MEMBER,
            "Un membre d'un groupe a été transferé vers un autre groupe",
        ),
        (
            TYPE_NEW_MEMBERS_THROUGH_TRANSFER,
            "De nouveaux membres ont été transferés vers le groupe",
        ),
        (TYPE_GROUP_CREATION_CONFIRMATION, "Groupe créé"),
        (TYPE_EVENT_SUGGESTION, "Événement suggéré"),
        (
            TYPE_REMINDER_DOCS_EVENT_EVE,
            "Rappel à la veille d'un événement des documents à envoyer",
        ),
        (
            TYPE_REMINDER_DOCS_EVENT_NEXTDAY,
            "Rappel au lendemain d'un événement des documents à envoyer",
        ),
        (
            TYPE_REMINDER_REPORT_FORM_FOR_EVENT,
            "Rappel au lendemain d'un événement de l'éventuel formulaire de bilan à remplir",
        ),
        (
            TYPE_REMINDER_UPCOMING_EVENT_START,
            "Rappel du début imminent d'un événement pour les participants",
        ),
    )

    STATUS_UNDISPLAYED = "U"
    STATUS_DISPLAYED = "S"
    STATUS_INTERACTED = "I"
    STATUS_CHOICES = (
        (STATUS_UNDISPLAYED, "Pas encore présentée au destinataire"),
        (STATUS_DISPLAYED, "Présentée au destinataire"),
        (STATUS_INTERACTED, "Le destinataire a interagi avec"),
    )  # attention : l'ordre croissant par niveau d'interaction est important
    PUSH_STATUS_CHOICES = (
        (STATUS_UNDISPLAYED, "Pas énvoyée au destinataire"),
        (STATUS_DISPLAYED, "Envoyée au destinataire"),
        (STATUS_INTERACTED, "Cliquée par le destinataire"),
    )  # attention : l'ordre croissant par niveau d'interaction est important

    objects = ActivityManager()

    timestamp = models.DateTimeField(
        verbose_name="Date de la notification", null=False, default=timezone.now
    )

    type = models.CharField("Type", max_length=50, choices=TYPE_CHOICES)

    recipient = models.ForeignKey(
        "people.Person",
        on_delete=models.CASCADE,
        related_name="activities",
        related_query_name="activities",
    )

    status = models.CharField(
        "Statut", max_length=1, choices=STATUS_CHOICES, default=STATUS_UNDISPLAYED
    )

    push_status = models.CharField(
        "Statut notification push",
        max_length=1,
        choices=PUSH_STATUS_CHOICES,
        default=STATUS_UNDISPLAYED,
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
