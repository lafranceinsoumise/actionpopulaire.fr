import pandas as pd
from django.utils import timezone

from agir.payments.models import Subscription, Payment
from agir.people.models import Person


def get_end_date_from_datetime(end_date):
    if not isinstance(end_date, timezone.datetime):
        return end_date

    # Force datetime to last day of the month
    end_date = end_date.replace(
        day=28, hour=23, minute=59, second=59, microsecond=0
    ).astimezone(timezone.utc)
    following_month = end_date + timezone.timedelta(days=4)
    end_date = following_month - timezone.timedelta(days=following_month.day)

    return end_date.isoformat()[0:10]


def monthly_to_single_time_contribution(data):
    today = timezone.now().isoformat()[0:10]
    # The multiplier is the number of month ends between today and the end date
    multiplier = len(
        pd.date_range(
            start=today,
            end=data.get("end_date"),
            freq="M",
        )
    )
    data["amount"] *= multiplier
    if data.get("allocations"):
        data["allocations"] = [
            {**allocation, "amount": allocation["amount"] * multiplier}
            for allocation in data.get("allocations")
        ]

    return data


def can_make_contribution(email=None, person=None):
    from agir.donations.apps import DonsConfig

    if not email and not person:
        return False

    if not person:
        try:
            person = Person.objects.get_by_natural_key(email)
        except Person.DoesNotExist:
            return True

    if Subscription.objects.filter(
        status=Subscription.STATUS_ACTIVE,
        type=DonsConfig.CONTRIBUTION_TYPE,
        person=person,
    ).exists():
        return False

    if (
        Payment.objects.exclude(meta__end_date__isnull=True)
        .filter(
            status=Payment.STATUS_COMPLETED,
            type=DonsConfig.CONTRIBUTION_TYPE,
            email__in=person.emails.values_list("address", flat=True),
            # TODO: handle renewals from september on (this condition will prevent them)
            meta__end_date__gte=timezone.now().isoformat(),
        )
        .exists()
    ):
        return False

    return True
