import datetime

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

    def aggregate_for_period(self, start=None, end=None):
        qs = self.order_by("-date")

        if start:
            qs = qs.filter(date__gte=start)

        if end:
            qs = qs.filter(date__lte=end)

        first = qs.last()
        last = qs.first()
        aggregates = {"period": (first.date, last.date)}

        for key in self.model.AGGREGATABLE_FIELDS:
            aggregates[key] = getattr(last, key) - getattr(first, key)

        return aggregates

    def aggregate_for_last_week(self):
        today = datetime.date.today()
        last_monday = today - datetime.timedelta(days=today.weekday(), weeks=1)
        last_sunday = last_monday + datetime.timedelta(days=6)
        return self.aggregate_for_period(last_monday, last_sunday)

    def aggregate_for_last_week_progress(self):
        last_week = self.aggregate_for_last_week()
        last_monday, last_sunday = last_week["period"]
        previous_monday = last_monday - datetime.timedelta(weeks=1)
        previous_sunday = last_sunday - datetime.timedelta(weeks=1)
        previous_week = self.aggregate_for_period(previous_monday, previous_sunday)
        aggregates = {"period": last_week["period"]}

        for key in self.model.AGGREGATABLE_FIELDS:
            aggregates[key] = last_week[key] - previous_week[key]

        return aggregates

    def aggregate_for_current_month(self, date=None):
        if date is None:
            date = datetime.date.today()
        return self.filter(
            date__year=date.year, date__month=date.month
        ).aggregate_for_period()

    def aggregate_for_current_year(self, date=None):
        if date is None:
            date = datetime.date.today()
        return self.filter(date__year=date.year).aggregate_for_period()


class AbsoluteStatistics(TimeStampedModel):
    AGGREGATABLE_FIELDS = (
        "event_count",
        "local_supportgroup_count",
        "local_certified_supportgroup_count",
        "membership_person_count",
        "boucle_departementale_membership_person_count",
        "political_support_person_count",
        "lfi_newsletter_subscriber_count",
        "sent_campaign_count",
        "sent_campaign_email_count",
    )

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
    boucle_departementale_membership_person_count = models.IntegerField(
        verbose_name="Membres des boucles départementales",
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
        get_latest_by = "date"
