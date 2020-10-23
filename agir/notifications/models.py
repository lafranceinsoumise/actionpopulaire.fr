from django.conf import settings
from django.db import models
from django.db.models import Q
from django.urls import reverse
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
    STATUS_UNSEEN = "U"
    STATUS_SEEN = "S"
    STATUS_CLICKED = "C"
    STATUS_CHOICES = (
        (STATUS_UNSEEN, "Non vue"),
        (STATUS_SEEN, "Vue"),
        (STATUS_CLICKED, "Cliquée"),
    )

    person = models.ForeignKey(
        "people.Person",
        on_delete=models.CASCADE,
        related_name="notifications",
        related_query_name="notification",
    )

    announcement = models.ForeignKey(
        Announcement,
        on_delete=models.CASCADE,
        related_name="notifications",
        related_query_name="notification",
        null=True,
    )

    status = models.CharField(
        "Status", max_length=1, choices=STATUS_CHOICES, default=STATUS_UNSEEN
    )

    icon = models.CharField(
        verbose_name="icône",
        max_length=200,
        help_text=format_html(
            'Indiquez le nom d\'une icône dans <a href="{icon_link}">cette liste</a>',
            icon_link="https://fontawesome.com/v4.7.0/icons/",
        ),
        blank=True,
    )

    content = DescriptionField(
        verbose_name=_("Contenu de la notification"),
        allowed_tags=["p", "div", "strong", "em", "a", "br"],
        blank=True,
    )
    link = models.URLField(verbose_name=_("Lien"), blank=True)

    def get_absolute_url(self):
        return reverse("follow_notification", kwargs={"pk": self.id})

    class Meta:
        indexes = [
            models.Index(
                fields=["link"],
                name="internal_links",
                condition=Q(link__startswith=settings.FRONT_DOMAIN),
            )
        ]
        unique_together = ("announcement", "person")
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(content__isnull=False)
                    | models.Q(announcement__isnull=False)
                )
                & (models.Q(icon__isnull=False) | models.Q(announcement__isnull=False)),
                name="has_content",
            )
        ]
        ordering = ("-created",)
