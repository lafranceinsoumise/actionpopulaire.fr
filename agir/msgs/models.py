import reversion
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from stdimage import StdImageField

from agir.lib.models import TimeStampedModel, BaseAPIResource


class UserReport(TimeStampedModel):
    reporter = models.ForeignKey(
        "people.Person",
        on_delete=models.SET_NULL,
        verbose_name="Personne à l'origine du signalement",
        null=True,
    )

    content_type = models.ForeignKey(
        ContentType, on_delete=models.PROTECT, verbose_name="Type"
    )
    object_id = models.UUIDField()
    reported_object = GenericForeignKey()

    class Meta:
        verbose_name = "Signalement"
        verbose_name_plural = "Signalements"


class AbstractMessage(BaseAPIResource):
    author = models.ForeignKey(
        "people.Person",
        editable=False,
        on_delete=models.SET_NULL,
        verbose_name="Auteur",
        null=True,
    )
    text = models.TextField("Contenu", max_length=2000)
    image = StdImageField()
    reports = GenericRelation(UserReport)
    deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True


@reversion.register()
class SupportGroupMessage(AbstractMessage):
    subject = models.TextField(
        "Objet", max_length=2000, null=False, blank=True, default=""
    )
    supportgroup = models.ForeignKey(
        "groups.SupportGroup",
        editable=False,
        on_delete=models.PROTECT,
        verbose_name="Groupe / équipe",
        related_name="messages",
    )
    linked_event = models.ForeignKey(
        "events.Event",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        verbose_name="Événement lié",
    )

    class Meta:
        verbose_name = "Message de groupe"
        verbose_name_plural = "Messages de groupe"


@reversion.register()
class SupportGroupMessageComment(AbstractMessage):
    message = models.ForeignKey(
        "SupportGroupMessage",
        on_delete=models.PROTECT,
        verbose_name="Message initial",
        related_name="comments",
    )

    class Meta:
        verbose_name = "Commentaire de messages de groupe"
        verbose_name_plural = "Commentaires de messages de groupe"


class SupportGroupMessageRecipient(TimeStampedModel):
    recipient = models.ForeignKey(
        "people.Person",
        on_delete=models.CASCADE,
        verbose_name="Destinataire",
        related_name="read_messages",
        null=False,
    )
    message = models.ForeignKey(
        "SupportGroupMessage",
        on_delete=models.CASCADE,
        verbose_name="Message",
        related_name="readers",
        null=False,
    )

    def __str__(self):
        return _("{recipient} --> {message}").format(
            recipient=self.recipient, message=self.message,
        )

    @property
    def unread_comments(self):
        if self.message.deleted:
            return self.message.comments.none()
        return self.message.comments.exclude(author_id=self.recipient.id).filter(
            created__gt=self.modified
        )

    class Meta:
        verbose_name = "Message lu par l'utilisateur·ice"
        verbose_name_plural = "Messages lus par les utilisateur·ices"
        constraints = [
            models.UniqueConstraint(
                fields=["recipient", "message"],
                name="unique_for_message_and_recipient",
            ),
        ]
