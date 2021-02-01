import reversion
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from stdimage import StdImageField

from agir.lib.models import TimeStampedModel, BaseAPIResource


class UserReport(TimeStampedModel):
    reporter = models.ForeignKey(
        "people.Person",
        on_delete=models.PROTECT,
        verbose_name="Personne à l'origine du signalement",
    )

    content_type = models.ForeignKey(
        ContentType, on_delete=models.PROTECT, verbose_name="Type"
    )
    object_id = models.UUIDField()
    reported_object = GenericForeignKey()


class AbstractMessage(BaseAPIResource):
    author = models.ForeignKey(
        "people.Person", editable=False, on_delete=models.PROTECT, verbose_name="Auteur"
    )
    text = models.TextField("Contenu", max_length=2000)
    image = StdImageField()
    reports = GenericRelation(UserReport)

    class Meta:
        abstract = True


@reversion.register()
class SupportGroupMessage(AbstractMessage):
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
