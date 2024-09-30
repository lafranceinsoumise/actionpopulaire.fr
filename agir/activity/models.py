import dynamic_filenames
from django.conf import settings
from django.core import validators
from django.core.validators import FileExtensionValidator
from django.db import models, transaction
from django.utils import timezone
from django.utils.functional import cached_property
from push_notifications.models import GCMDevice
from firebase_admin import messaging
from stdimage import StdImageField
from stdimage.validators import MinSizeValidator

from agir.lib.models import TimeStampedModel, DescriptionField, BaseAPIResource
from agir.lib.utils import front_url, is_absolute_url

__all__ = ["Activity", "Announcement", "PushAnnouncement"]

from agir.lib.validators import FileSizeValidator


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
    TYPE_PUSH_ANNOUNCEMENT = "push-announcement"
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
    TYPE_NEW_EVENT_SPEAKER_REQUEST = "new-event-speaker-request"

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
    TYPE_UNCERTIFIABLE_GROUP_WARNING = "uncertifiable-group-warning"

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
        TYPE_NEW_EVENT_SPEAKER_REQUEST,
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
        (TYPE_NEW_EVENT_SPEAKER_REQUEST, "Nouvelle demande d'événement reçue"),
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
        (
            TYPE_UNCERTIFIABLE_GROUP_WARNING,
            "Avertissement aux animateur·ices d'un groupe certifié qui ne respecte plus les critères de certification",
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
        blank=True,
    )

    supportgroup = models.ForeignKey(
        "groups.SupportGroup",
        on_delete=models.CASCADE,
        related_name="notifications",
        related_query_name="notification",
        null=True,
        blank=True,
    )

    individual = models.ForeignKey(
        "people.Person",
        on_delete=models.CASCADE,
        related_name="+",
        null=True,
        blank=True,
    )

    announcement = models.ForeignKey(
        "Announcement",
        on_delete=models.CASCADE,
        related_name="activities",
        related_query_name="activity",
        null=True,
        blank=True,
    )
    push_announcement = models.ForeignKey(
        "PushAnnouncement",
        on_delete=models.CASCADE,
        related_name="activities",
        related_query_name="activity",
        null=True,
        blank=True,
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
            models.UniqueConstraint(
                fields=["recipient", "push_announcement"],
                condition=models.Q(type="push_announcement"),
                name="unique_for_recipient_and_push_announcement",
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


class PushAnnouncement(BaseAPIResource):
    title = models.CharField(
        verbose_name="Titre",
        max_length=50,
        blank=True,
        default="",
        help_text="Max. 50 caractères.",
    )

    subtitle = models.CharField(
        verbose_name="Sous-titre",
        max_length=60,
        blank=True,
        default="",
        help_text="Max. 60 caractères. Le sous-titre s'affichera uniquement sur iOS.",
    )

    message = models.TextField(
        verbose_name="Message",
        blank=False,
        help_text="Longueur max. conséillée env. 150 caractères sur iOS et 240 sur Android.",
    )

    link = models.URLField(
        verbose_name="Lien",
        blank=False,
        help_text="Le lien à ouvrir lors du clic sur la notification.",
    )

    image = StdImageField(
        verbose_name="Image",
        validators=[
            FileSizeValidator(5 * 1024 * 1024),
            FileExtensionValidator(["jpg", "jpeg"]),
        ],
        upload_to=dynamic_filenames.FilePattern(
            filename_pattern="activity/pushannouncements/image/{uuid:.2base32}/{uuid:s}{ext}"
        ),
        null=True,
        blank=True,
        help_text="Utiliser une image au format JPEG avec un ratio de 2:1 et de maximum 5 MB.",
    )

    thread_id = models.CharField(
        verbose_name="Idéntifiant de groupe",
        max_length=64,
        blank=True,
        default="",
        help_text="Max. 64 caractères. Si indiqué, permet de regrouper les notifications avec le même "
        "identifiant de groupe ensemble.",
    )

    ttl = models.IntegerField(
        verbose_name="Durée de vie (en secondes)",
        validators=[
            validators.MinValueValidator(1),
            validators.MaxValueValidator(2419200),  # 28 days
        ],
        blank=False,
        default=259200,  # 3 days
        help_text="Max. 28 jours. La notification ne sera pas reçue si l'appareil n'est "
        "pas connecté au réseau pendant le temps indiqué.",
    )

    segment = models.ForeignKey(
        to="mailing.Segment",
        verbose_name="Segment",
        on_delete=models.CASCADE,
        related_name="push_notifications",
        related_query_name="push_notification",
        null=False,
        blank=False,
        help_text="Segment des personnes auquel ce message sera envoyé.",
    )

    test_segment = models.ForeignKey(
        to="mailing.Segment",
        verbose_name="Segment",
        on_delete=models.SET_NULL,
        related_name="+",
        related_query_name="+",
        null=True,
        blank=True,
        help_text="Segment des personnes auxquelles envoyer des notifications de test",
    )

    has_ios = models.BooleanField(
        verbose_name="Envoyer aux appareils iOS", default=True, blank=False
    )

    has_android = models.BooleanField(
        verbose_name="Envoyer aux appareils Android", default=True, blank=False
    )

    sending_meta = models.JSONField(
        "Résultats de l'envoi", blank=True, default=dict, editable=False
    )
    sending_date = models.DateTimeField(
        "Date d'envoi",
        null=True,
        default=None,
        editable=False,
    )

    @cached_property
    def subscribers(self):
        return self.segment.get_people()

    @cached_property
    def android_recipient_device_count(self):
        return self.get_gcm_subscriber_devices(self.segment).count()

    @cached_property
    def ios_recipient_device_count(self):
        return self.get_ios_subscriber_devices(self.segment).count()

    @cached_property
    def recipient_device_count(self):
        return self.android_recipient_device_count + self.ios_recipient_device_count

    @cached_property
    def recipient_ids(self):
        return list(
            set(
                self.get_gcm_subscriber_devices(self.segment)
                .values_list("user__person__id", flat=True)
                .union(
                    self.get_ios_subscriber_devices(self.segment).values_list(
                        "user__person__id", flat=True
                    )
                )
            )
        )

    @cached_property
    def test_recipient_ids(self):
        if not self.test_segment:
            return []

        return list(
            set(
                self.get_gcm_subscriber_devices(self.test_segment)
                .values_list("user__person__id", flat=True)
                .union(
                    self.get_ios_subscriber_devices(self.test_segment).values_list(
                        "user__person__id", flat=True
                    )
                )
            )
        )

    def get_gcm_subscriber_devices(self, segment):
        if not self.has_android:
            return GCMDevice.objects.none()
        subscribers = segment.get_people()
        return GCMDevice.objects.filter(
            active=True, user__is_active=True, user__person__in=subscribers
        )

    def recipient_count(self):
        return len(self.recipient_ids)

    def test_recipient_count(self):
        return len(self.test_recipient_ids)

    def displayed_count(self):
        return self.activities.filter(
            push_status__in=(Activity.STATUS_DISPLAYED, Activity.STATUS_INTERACTED)
        ).count()

    def clicked_count(self):
        return self.activities.filter(push_status=Activity.STATUS_INTERACTED).count()

    def get_absolute_image_url(self):
        if not self.image:
            return None

        image_url = self.image.storage.url(self.image.name)
        if not is_absolute_url(image_url):
            image_url = settings.FRONT_DOMAIN + image_url

        return image_url

    def get_link_url(self):
        return front_url(
            "activity:push_announcement_link", args=[self.pk], absolute=True
        )

    def get_fcm_kwargs(self):
        """Generate payload as FCM message
        Handle android & iOS devices"""

        return messaging.Message(
            data={"url": self.get_link_url()},
            notification=messaging.Notification(
                title=self.title, body=self.message, image=self.get_absolute_image_url()
            ),
            android=messaging.AndroidConfig(ttl=self.ttl, collapse_key=str(self.id)),
            apns=messaging.APNSConfig(
                headers={
                    "apns-expiration": str(self.ttl),
                    "apns-collapse-id": str(self.id),
                }
            ),
        )

    def can_send(self):
        return self.sending_date is None

    def push(self, segment=None):
        if segment is None:
            segment = self.segment

        # Get notification payloads
        notification_message = self.get_fcm_kwargs()

        # Send messages
        gcm_devices = self.get_gcm_subscriber_devices(segment)

        try:
            reponse = gcm_devices.send_message(notification_message)
        except Exception as e:
            response = f"Exception: {str(e)}"

        return {
            "segment": f"{segment.name} [#{segment.id}]",
            "recipients": gcm_devices.count(),
        }

    def send(self):
        if not self.can_send():
            raise Exception("Cette annonce a déjà été envoyée")

        recipient_count = self.recipient_count()

        if recipient_count == 0:
            raise Exception(
                "Aucun destinataire n'a été trouvé pour le segment spécifié"
            )

        sending_result = self.push()

        with transaction.atomic():
            # Create activities
            Activity.objects.bulk_create(
                [
                    Activity(
                        type=Activity.TYPE_PUSH_ANNOUNCEMENT,
                        recipient_id=recipient_id,
                        push_announcement_id=self.id,
                        status=Activity.STATUS_UNDISPLAYED,
                        push_status=Activity.STATUS_DISPLAYED,
                    )
                    for recipient_id in self.recipient_ids
                ],
                ignore_conflicts=True,
            )

            # Update sending data
            self.sending_date = timezone.now()
            self.sending_meta = sending_result
            self.save()

    def test(self):
        if not self.test_segment:
            raise Exception("Aucun segment de test n'a été défini.")

        return self.push(self.test_segment)

    def __str__(self):
        if self.title:
            return f"Annonce push « {self.title} »"

        return f"Annonce push #{self.id}"

    class Meta:
        verbose_name = "Annonce push"
        verbose_name_plural = "Annonces push"
        ordering = ("-created",)
