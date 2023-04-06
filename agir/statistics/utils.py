import datetime

from nuntius.models import CampaignSentEvent

from agir.events.models import Event
from agir.groups.models import SupportGroup, Membership
from agir.lib.materiel import MaterielRestAPI
from agir.people.models import Person


def get_absolute_statistics(date=None, as_kwargs=False):
    if date is None:
        date = datetime.date.today() - datetime.timedelta(days=1)

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
        "political_support_person_count": Person.objects.with_active_role()
        .is_political_support()
        .filter(created__date__lte=date),
        "lfi_newsletter_subscriber_count": (
            Person.objects.with_active_role()
            .filter(newsletters__contains=(Person.NEWSLETTER_2022,))
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
    }

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


def get_materiel_statistics(date=None):
    if date is None:
        date = datetime.date.today() - datetime.timedelta(days=1)

    api = MaterielRestAPI()
    data = api.retrieve_sales_report(date_min=date, date_max=date)
    data = {
        key: round(float(value) * 100) if isinstance(value, str) else value
        for key, value in data.items()
        if key in MATERIEL_SALES_REPORT_FIELDS
    }
    data["date"] = date

    return data
