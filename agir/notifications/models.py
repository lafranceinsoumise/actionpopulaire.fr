from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from agir.lib.html import sanitize_html
from agir.lib.models import DescriptionField


class NotificationQuerySet(models.QuerySet):
    def active(self):
        now = timezone.now()

        return self.filter(
            (models.Q(start_date__isnull=True) | models.Q(start_date__lt=now))
            & (models.Q(end_date__isnull=True) | models.Q(end_date__gt=now))
        )


class Notification(models.Model):

    objects = NotificationQuerySet.as_manager()

    content = DescriptionField(
        verbose_name=_("Contenu de la notification"),
        allowed_tags=["p", "div", "strong", "em", "a", "br"],
    )
    link = models.URLField(verbose_name=_("Lien"))
    start_date = models.DateTimeField(
        verbose_name=_("Date de début"), null=True, blank=True
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
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")
        indexes = (
            models.Index(
                fields=("start_date", "end_date"), name="notification_query_index"
            ),
        )
        ordering = ("start_date", "end_date")

    def get_absolute_url(self):
        return reverse("follow_notification", kwargs={"pk": self.id})


class NotificationStatus(models.Model):
    STATUS_SEEN = "S"
    STATUS_CLICKED = "C"
    STATUS_CHOICES = ((STATUS_SEEN, "Vu"), (STATUS_CLICKED, "C"))

    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name="statuses",
        related_query_name="status",
    )

    person = models.ForeignKey(
        "people.Person",
        on_delete=models.CASCADE,
        related_name="notification_statuses",
        related_query_name="notification_status",
    )

    status = models.CharField("Status", max_length=1, choices=STATUS_CHOICES)

    class Meta:
        unique_together = ("notification", "person")
