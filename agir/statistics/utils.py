import datetime

from data_france.models import Commune
from django.db.models import Q, Case, When, Subquery, OuterRef, IntegerField, Count
from nuntius.models import CampaignSentEvent, CampaignSentStatusType

from agir.events.models import Event
from agir.groups.models import SupportGroup, Membership
from agir.lib.materiel import MaterielRestAPI
from agir.people.models import Person

POPULATION_RANGE_STEPS = [0, 1, 5, 10, 15, 20, 50, 100]
POPULATION_RANGES = [
    (i[0] * 1000, i[1] * 1000 - 1) if i[1] else (i[0] * 1000,)
    for i in zip(POPULATION_RANGE_STEPS, POPULATION_RANGE_STEPS[1:] + [False])
]


def get_default_date():
    return datetime.date.today() - datetime.timedelta(days=1)


def get_absolute_statistics(date=None, as_kwargs=False, columns=None):
    if date is None:
        date = get_default_date()

    querysets = {
        # EVENTS
        "event_count": Event.objects.public()
        .listed()
        .filter(start_time__date__lte=date),
        # GROUPS
        "local_supportgroup_count": (
            SupportGroup.objects.active()
            .filter(type=SupportGroup.TYPE_LOCAL_GROUP)
            .filter(created__date__lte=date)
        ),
        "local_certified_supportgroup_count": (
            SupportGroup.objects.active()
            .filter(type=SupportGroup.TYPE_LOCAL_GROUP)
            .certified()
            .filter(certification_date__date__lte=date)
        ),
        "membership_person_count": (
            Membership.objects.active()
            .filter(created__date__lte=date)
            .filter(supportgroup__type=SupportGroup.TYPE_LOCAL_GROUP)
            .distinct("person_id")
            .order_by("person_id")
        ),
        "boucle_departementale_membership_person_count": (
            Membership.objects.active()
            .filter(created__date__lte=date)
            .filter(supportgroup__type=SupportGroup.TYPE_BOUCLE_DEPARTEMENTALE)
            .distinct("person_id")
            .order_by("person_id")
        ),
        # PEOPLE
        "political_support_person_count": Person.objects.exclude(role__is_active=False)
        .is_political_support()
        .filter(created__date__lte=date),
        "liaison_count": (
            Person.objects.exclude(role__is_active=False)
            .liaisons()
            .filter(liaison_date__date__lte=date)
        ),
        "lfi_newsletter_subscriber_count": (
            Person.objects.exclude(role__is_active=False)
            .filter(newsletters__contains=(Person.Newsletter.LFI_REGULIERE,))
            .filter(created__date__lte=date)
        ),
        # MAILING
        "sent_campaign_count": CampaignSentEvent.objects.filter(
            datetime__date__lte=date
        )
        .distinct("campaign_id")
        .order_by("campaign_id"),
        "sent_campaign_email_count": CampaignSentEvent.objects.filter(
            datetime__date__lte=date
        ),
        "undelivered_campaign_email_count": CampaignSentEvent.objects.exclude(
            result__in=(
                CampaignSentStatusType.PENDING,
                CampaignSentStatusType.OK,
                CampaignSentStatusType.UNKNOWN,
            )
        ).filter(datetime__date__lte=date),
    }

    if columns:
        querysets = {key: qs for key, qs in querysets.items() if key in columns}

    if not querysets:
        return querysets

    if as_kwargs:
        querysets = {key: qs.count() for key, qs in querysets.items()}
        querysets["date"] = date

    return querysets


MATERIEL_SALES_REPORT_FIELDS = (
    "total_orders",
    "total_items",
    "total_customer",
    "total_sales",
    "net_sales",
    "average_sales",
    "total_tax",
    "total_shipping",
    "total_refunds",
    "total_discount",
)


def get_materiel_statistics(date=None, columns=None):
    if date is None:
        date = get_default_date()

    api = MaterielRestAPI()
    data = api.retrieve_sales_report(date_min=date, date_max=date)
    data = {
        key: round(float(value) * 100) if isinstance(value, str) else value
        for key, value in data.items()
        if key in MATERIEL_SALES_REPORT_FIELDS
    }

    if columns:
        data = {key: val for key, val in data.items() if key in columns}

    if data:
        data["date"] = date

    return data


def get_commune_queryset():
    return Commune.objects.filter(
        type__in=(Commune.TYPE_COMMUNE, Commune.TYPE_ARRONDISSEMENT_PLM)
    )


def get_commune_count_by_population_range(
    commune_qs=None, population_fieldname="population"
):
    if commune_qs is None:
        commune_qs = get_commune_queryset()
        population_fieldname = "population_municipale"

    return {
        "total": commune_qs.count(),
        **{
            population_range: commune_qs.filter(
                **{f"{population_fieldname}__range": population_range}
            ).count()
            if len(population_range) == 2
            else commune_qs.filter(
                **{f"{population_fieldname}__gte": population_range[0]}
            ).count()
            for population_range in POPULATION_RANGES
        },
    }


def get_commune_filter(commune):
    f = ~Q(location_citycode="") & Q(location_citycode=commune.code)
    f |= ~Q(location_zip="") & Q(
        location_zip__in=commune.codes_postaux.values_list("code", flat=True)
    )

    if commune.geometry:
        f |= ~Q(coordinates__isnull=True) & Q(coordinates__intersects=commune.geometry)

    return f


def count_by_commune_id(qs):
    communes = get_commune_queryset()
    return (
        qs.annotate(
            commune_id=Case(
                When(
                    ~Q(location_citycode=""),
                    then=Subquery(
                        communes.filter(code=OuterRef("location_citycode")).values("id")
                    ),
                ),
                When(
                    ~Q(location_zip=""),
                    then=Subquery(
                        communes.filter(
                            codes_postaux__code=OuterRef("location_zip")
                        ).values("id")[:1]
                    ),
                ),
                When(
                    Q(coordinates__isnull=False),
                    then=Subquery(
                        communes.filter(geometry__isnull=False)
                        .filter(geometry__intersects=OuterRef("coordinates"))
                        .values("id")[:1]
                    ),
                ),
                default=None,
                output_field=IntegerField(null=True),
            )
        )
        .filter(commune_id__isnull=False)
        .values("commune_id")
        .order_by("commune_id")
        .annotate(count=Count("pk", distinct=True))
    )


def get_commune_statistics(date=None, as_kwargs=False, columns=None):
    if date is None:
        date = get_default_date()

    querysets = {
        # EVENTS
        "event_count": Event.objects.public()
        .listed()
        .filter(start_time__date__lte=date),
        # GROUPS
        "local_supportgroup_count": (
            SupportGroup.objects.active()
            .filter(type=SupportGroup.TYPE_LOCAL_GROUP)
            .filter(created__date__lte=date)
        ),
        "local_certified_supportgroup_count": (
            SupportGroup.objects.active()
            .filter(type=SupportGroup.TYPE_LOCAL_GROUP)
            .certified()
            .filter(certification_date__date__lte=date)
        ),
        # PEOPLE
        "people_count": Person.objects.exclude(role__is_active=False).filter(
            created__date__lte=date
        ),
    }

    querysets = {
        key: count_by_commune_id(qs)
        for key, qs in querysets.items()
        if not columns or key in columns
    }

    statistics = {}
    for key, aggregate in querysets.items():
        for commune_id, count in aggregate.values_list("commune_id", "count"):
            if not commune_id in statistics:
                statistics[commune_id] = (
                    {"date": date, "commune_id": commune_id} if as_kwargs else {}
                )
            statistics[commune_id][key] = count

    communes = Commune.objects.filter(pk__in=statistics.keys()).only(
        "id", "population_municipale"
    )

    for commune in communes:
        statistics[commune.id]["population"] = commune.population_municipale

    return statistics.values()
