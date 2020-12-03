from django.db import models
from django.utils import timezone

from agir.lib.models import TimeStampedModel


class Activity(TimeStampedModel):
    # DONE
    TYPE_GROUP_INVITATION = "group-invitation"
    TYPE_NEW_MEMBER = "new-member"
    TYPE_GROUP_INFO_UPDATE = "group-info-update"
    TYPE_NEW_ATTENDEE = "new-attendee"
    TYPE_EVENT_UPDATE = "event-update"
    TYPE_NEW_EVENT_MYGROUPS = "new-event-mygroups"
    TYPE_NEW_REPORT = "new-report"
    TYPE_CANCELLED_EVENT = "cancelled-event"
    # TODO
    TYPE_GROUP_COORGANIZATION_INFO = "group-coorganization-info"
    TYPE_NEW_EVENT_AROUNDME = "new-event-aroundme"
    TYPE_ACCEPTED_INVITATION_MEMBER = "accepted-invitation-member"
    TYPE_GROUP_COORGANIZATION_ACCEPTED = "group-coorganization-accepted"
    TYPE_WAITING_LOCATION_EVENT = "waiting-location-event"
    TYPE_GROUP_COORGANIZATION_INVITE = "group-coorganization-invite"
    TYPE_WAITING_LOCATION_GROUP = "waiting-location-group"
    TYPE_WAITING_PAYMENT = "waiting-payment"

    TYPE_CHOICES = (
        (TYPE_WAITING_PAYMENT, "Paiement en attente"),
        (TYPE_GROUP_INVITATION, "Invitation à un groupe"),
        (TYPE_NEW_MEMBER, "Nouveau membre"),
        (TYPE_WAITING_LOCATION_GROUP, "Préciser la localisation du groupe"),
        (TYPE_GROUP_COORGANIZATION_INVITE, "Invitation à coorganiser un groupe reçue"),
        (TYPE_WAITING_LOCATION_EVENT, "Préciser la localisation d'un évènement"),
        (
            TYPE_GROUP_COORGANIZATION_ACCEPTED,
            "Invitation à coorganiser un groupe acceptée",
        ),
        (TYPE_GROUP_INFO_UPDATE, "Mise à jour des informations du groupe"),
        (TYPE_ACCEPTED_INVITATION_MEMBER, "Invitation à rejoindre un groupe acceptée"),
        (TYPE_NEW_ATTENDEE, "Un nouveau participant à votre évènement"),
        (TYPE_EVENT_UPDATE, "Mise à jour d'un évènement"),
        (TYPE_NEW_EVENT_MYGROUPS, "Votre groupe organise un évènement"),
        (TYPE_NEW_REPORT, "Nouveau compte-rendu d'évènement"),
        (TYPE_NEW_EVENT_AROUNDME, "Nouvel évènement près de chez moi"),
        (TYPE_CANCELLED_EVENT, "Événement annulé"),
    )

    STATUS_UNDISPLAYED = "U"
    STATUS_DISPLAYED = "S"
    STATUS_INTERACTED = "I"
    STATUS_CHOICES = (
        (STATUS_UNDISPLAYED, "Pas encore présentée au destinataire"),
        (STATUS_DISPLAYED, "Présentée au destinataire"),
        (STATUS_INTERACTED, "Le destinataire a interagi avec"),
    )

    timestamp = models.DateTimeField(
        verbose_name="Date de la notification", null=False, default=timezone.now
    )

    type = models.CharField("Type", max_length=50, choices=TYPE_CHOICES)

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

    individual = models.ForeignKey(
        "people.Person", on_delete=models.CASCADE, related_name="+", null=True
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
