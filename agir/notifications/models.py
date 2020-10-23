from django.db import models
from django.db.models.fields.json import JSONField
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from agir.lib.html import sanitize_html
from agir.lib.models import DescriptionField, TimeStampedModel


class AnnouncementQuerySet(models.QuerySet):
    def active(self):
        now = timezone.now()

        return self.filter(
            (models.Q(start_date__lt=now))
            & (models.Q(end_date__isnull=True) | models.Q(end_date__gt=now))
        )


class Announcement(models.Model):
    objects = AnnouncementQuerySet.as_manager()

    icon = models.CharField(
        verbose_name="icône",
        max_length=200,
        default="exclamation",
        help_text=format_html(
            'Indiquez le nom d\'une icône dans <a href="{icon_link}">cette liste</a>',
            icon_link="https://fontawesome.com/v4.7.0/icons/",
        ),
    )

    content = DescriptionField(
        verbose_name=_("Contenu de la notification"),
        allowed_tags=["p", "div", "strong", "em", "a", "br"],
    )
    link = models.URLField(verbose_name=_("Lien"), blank=True)

    start_date = models.DateTimeField(
        verbose_name=_("Date de début"), default=timezone.now
    )
    end_date = models.DateTimeField(
        verbose_name=_("Date de fin"), null=True, blank=True
    )
    segment = models.ForeignKey(
        to="mailing.Segment",
        on_delete=models.CASCADE,
        related_name="notifications",
        related_query_name="notification",
        null=True,
        blank=True,
        help_text=_(
            "Segment des personnes auquel ce message sera montré (laisser vide pour montrer à tout le monde)"
        ),
    )

    def __str__(self):
        no_tag_content = sanitize_html(self.content, tags=[])
        if len(no_tag_content) > 100:
            no_tag_content = no_tag_content[:97] + "..."

        return f"« {no_tag_content} »"

    class Meta:
        verbose_name = _("Annonce")
        indexes = (
            models.Index(
                fields=("start_date", "end_date"), name="notification_query_index"
            ),
        )
        ordering = ("start_date", "end_date")


class Notification(TimeStampedModel):
    TYPE_WAITING_PAYMENT = "waiting-payment"
    TYPE_GROUP_INVITATION = "group-invitation"
    TYPE_NEW_MEMBER = "new-member"
    TYPE_WAITING_LOCATION_GROUP = "waiting-location-group"
    TYPE_GROUP_COORGANIZATION_INVITE = "group-coorganization-invite"
    TYPE_WAITING_LOCATION_EVENT = "waiting-location-event"
    TYPE_GROUP_COORGANIZATION_ACCEPTED = "group-coorganization-accepted"
    TYPE_GROUP_INFO_UPDATE = "group-info-update"
    TYPE_ACCEPTED_INVITATION_MEMBER = "accepted-invitation-member"
    TYPE_NEW_ATTENDEE = "new_attendee"
    TYPE_EVENT_UPDATE = "event-update"
    TYPE_NEW_EVENT_MYGROUPS = "new-event-mygroups"
    TYPE_NEW_REPORT = "new-report"
    TYPE_NEW_EVENT_AROUNDME = "new-event-aroundme"
    TYPE_GROUP_COORGANIZATION_INFO = "group-coorganization-info"
    TYPE_CANCELLED_EVENT = "cancelled-event"

    TYPE_CHOICES = (
        (TYPE_WAITING_PAYMENT, "Paiement en attente"),
        (TYPE_GROUP_INVITATION, "Invitation à un groupe"),
        (TYPE_NEW_MEMBER, "Nouveau membre"),
        (TYPE_WAITING_LOCATION_GROUP, "Préciser la localisation du groupe"),
        (TYPE_GROUP_COORGANIZATION_INVITE, "Invitation à coorganiser un groupe reçue"),
        (TYPE_WAITING_LOCATION_EVENT, "Préciser la localisation d'un événement"),
        (
            TYPE_GROUP_COORGANIZATION_ACCEPTED,
            "Invitation à coorganiser un groupe acceptée",
        ),
        (TYPE_GROUP_INFO_UPDATE, "Mise à jour des informations du groupe"),
        (TYPE_ACCEPTED_INVITATION_MEMBER, "Invitation à rejoindre un groupe acceptée"),
        (TYPE_NEW_ATTENDEE, "Un nouveau participant à votre événement"),
        (TYPE_EVENT_UPDATE, "Mise à jour d'un événement"),
        (TYPE_NEW_EVENT_MYGROUPS, "Votre groupe organise un événement"),
        (TYPE_NEW_REPORT, "Nouveau compte-rendu d'événement"),
        (TYPE_NEW_EVENT_AROUNDME, "Nouvel événement près de chez moi"),
        (TYPE_CANCELLED_EVENT, "Événement annulé"),
    )

    STATUS_UNDISPLAYED = "U"
    STATUS_DISPLAYED = "S"
    STATUS_INTERACTED = "I"
    STATUS_CHOICES = (
        (STATUS_UNDISPLAYED, "Non affichée"),
        (STATUS_DISPLAYED, "Affichée"),
        (STATUS_INTERACTED, "Interagie"),
    )

    type = models.CharField("Type", max_length=50,)

    recipient = models.ForeignKey(
        "people.Person",
        on_delete=models.CASCADE,
        related_name="received_notifications",
        related_query_name="received_notification",
    )

    status = models.CharField(
        "Status", max_length=1, choices=STATUS_CHOICES, default=STATUS_UNDISPLAYED
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

    subject = models.ForeignKey(
        "people.Person", on_delete=models.CASCADE, related_name="+", null=True
    )

    meta = JSONField("Autres données", blank=True, default=dict)

    class Meta:
        ordering = ("-created",)
        indexes = (
            models.Index(
                fields=("recipient", "created"), name="notifications_by_recipient"
            ),
        )
