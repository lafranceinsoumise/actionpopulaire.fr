from django.db import models
from nuntius.models import CampaignSentEvent

from agir.events.models import Event
from agir.groups.models import SupportGroup, Membership
from agir.lib.models import TimeStampedModel
from agir.people.models import Person
from agir.statistics.utils import get_statistics_querysets


class AbsoluteStatisticsQueryset(models.QuerySet):
    def create(self, date=None, **kwargs):
        values = get_statistics_querysets(date, as_kwargs=True)
        kwargs.update(values)
        return super().create(**kwargs)

    def update_or_create(self, defaults=None, **kwargs):
        date = kwargs.pop("date", None)
        defaults = get_statistics_querysets(date, as_kwargs=True)
        date = defaults.pop("date")
        return super().update_or_create(date=date, defaults=defaults, **kwargs)


class AbsoluteStatistics(TimeStampedModel):
    objects = AbsoluteStatisticsQueryset.as_manager()

    date = models.DateField(
        verbose_name="Date",
        editable=False,
        unique=True,
        db_index=True,
    )
    event_count = models.IntegerField(
        verbose_name="Événements", null=False, blank=False, default=0
    )
    local_supportgroup_count = models.IntegerField(
        verbose_name="Groupes d'action locaux",
        null=False,
        blank=False,
        default=0,
    )
    local_certified_supportgroup_count = models.IntegerField(
        verbose_name="Groupes d'action locaux certifiés",
        null=False,
        blank=False,
        default=0,
    )
    political_support_person_count = models.IntegerField(
        verbose_name="Inscrits LFI", null=False, blank=False, default=0
    )
    membership_person_count = models.IntegerField(
        verbose_name="Membres de groupe d'action",
        null=False,
        blank=False,
        default=0,
    )
    lfi_newsletter_subscriber_count = models.IntegerField(
        verbose_name="Inscriptions à la lettre d'information LFI",
        null=False,
        blank=False,
        default=0,
    )
    sent_campaign_count = models.IntegerField(
        verbose_name="Campagnes e-mail envoyées",
        null=False,
        blank=False,
        default=0,
    )
    sent_campaign_email_count = models.IntegerField(
        verbose_name="E-mails envoyés", null=False, blank=False, default=0
    )

    def __str__(self):
        return f"Statistiques du {self.date}"

    class Meta:
        verbose_name = "statistique absolue"
        verbose_name_plural = "statistiques absolues"
        ordering = ("-date",)
        get_latest_by = "-date"
