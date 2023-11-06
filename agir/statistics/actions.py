import datetime

from django.db.models import Count, Q
from nuntius.models import Campaign
from tqdm import tqdm

from agir.statistics.models import (
    AbsoluteStatistics,
    MaterielStatistics,
    CommuneStatistics,
)
from agir.statistics.utils import (
    get_absolute_statistics,
    get_materiel_statistics,
    get_commune_statistics,
)


def get_largest_campaign_statistics(start, end):
    return list(
        Campaign.objects.filter(campaignsentevent__datetime__date__range=(start, end))
        .annotate(sent_email_count=Count("campaignsentevent__id"))
        .filter(sent_email_count__gte=10000)
        .annotate(
            open_email_count=Count(
                "campaignsentevent__id",
                filter=Q(campaignsentevent__open_count__gt=0),
            )
        )
        .values(
            "id",
            "name",
            "sent_email_count",
            "open_email_count",
        )
    )


def create_statistics_from_date(date=None, silent=False):
    today = datetime.date.today()
    if date is None:
        # defaults to current year start
        date = today.replace(day=1, month=1)

    progress = tqdm(
        total=(today - date).days,
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}]",
        colour="#cbbfec",
        disable=silent,
    )

    while date < today:
        progress.set_description_str(str(date))

        # Create AbsoluteStatistics
        abs_kwargs = get_absolute_statistics(date=date, as_kwargs=True)
        AbsoluteStatistics.objects.update_or_create(
            date=abs_kwargs.pop("date"), defaults=abs_kwargs
        )

        # Create MaterielStatistics
        mat_kwargs = get_materiel_statistics(date=date)
        MaterielStatistics.objects.update_or_create(
            date=mat_kwargs.pop("date"), defaults=mat_kwargs
        )

        # Create CommuneStatistics
        CommuneStatistics.objects.update_or_create_all_for_date(date=date)

        date += datetime.timedelta(days=1)
        progress.update(1)

    progress.clear()


def update_statistics_from_date(date=None, silent=False, columns=None):
    today = datetime.date.today()
    if date is None:
        # defaults to current year start
        date = today.replace(day=1, month=1)

    progress = tqdm(
        total=(today - date).days,
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}]",
        colour="#cbbfec",
        disable=silent,
    )

    while date < today:
        progress.set_description_str(str(date))

        # Update AbsoluteStatistics
        abs_kwargs = get_absolute_statistics(date=date, as_kwargs=True, columns=columns)
        if abs_kwargs:
            AbsoluteStatistics.objects.filter(date=date).update(**abs_kwargs)

        # Update MaterielStatistics
        mat_kwargs = get_materiel_statistics(date=date, columns=columns)
        if mat_kwargs:
            MaterielStatistics.objects.filter(date=date).update(**mat_kwargs)

        # Update CommuneStatistics
        commune_kwargs = get_commune_statistics(
            date=date, columns=columns, as_kwargs=True
        )
        if commune_kwargs:
            CommuneStatistics.objects.update_all_for_date(
                date=date, defaults=commune_kwargs
            )

        date += datetime.timedelta(days=1)
        progress.update(1)

    progress.clear()
