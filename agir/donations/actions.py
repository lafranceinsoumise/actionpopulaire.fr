import datetime

import pandas as pd
from dateutil.relativedelta import relativedelta
from django.conf import settings
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


def monthly_to_single_time_contribution(data, from_date=None):
    if from_date is None:
        from_date = timezone.now()

    from_date = from_date.isoformat()[0:10]

    # The multiplier is the number of month ends between today and the end date
    multiplier = len(
        pd.date_range(
            start=from_date,
            end=data.get("end_date"),
            freq="MS",
        )
    )
    data["amount"] *= multiplier
    if data.get("allocations"):
        data["allocations"] = [
            {**allocation, "amount": allocation["amount"] * multiplier}
            for allocation in data.get("allocations")
        ]

    return data


def single_time_to_monthly_contribution(data, from_date):
    # The multiplier is the number of month ends between today and the end date
    multiplier = len(
        pd.date_range(
            start=from_date,
            end=data.get("endDate"),
            freq="MS",
        )
    )
    data["amount"] /= multiplier
    if data.get("allocations"):
        data["allocations"] = [
            {**allocation, "amount": allocation["amount"] / multiplier}
            for allocation in data.get("allocations")
        ]

    return data


def get_active_contribution_for_person(person=None):
    if isinstance(person, str):
        try:
            person = Person.objects.get_by_natural_key(email=person)
        except Person.DoesNotExist:
            person = None

    if not person:
        return None

    monthly_subscription = (
        Subscription.objects.active_contributions()
        .filter(person=person)
        .order_by("-end_date")
        .first()
    )

    single_time_payment = (
        Payment.objects.active_contribution()
        .filter(email__in=person.emails.values_list("address", flat=True))
        .order_by("-meta__end_date")
        .first()
    )

    if not monthly_subscription:
        return single_time_payment

    if not single_time_payment or not single_time_payment.meta.get("end_date", None):
        return monthly_subscription

    if (
        monthly_subscription.end_date.strftime("%Y-%m-%d")
        >= single_time_payment.meta["end_date"]
    ):
        return monthly_subscription

    return single_time_payment


def get_contribution_end_date(contribution):
    end_date = None

    if isinstance(contribution, Subscription):
        end_date = contribution.end_date

    if isinstance(contribution, Payment):
        end_date = contribution.meta.get("end_date", None)
        end_date = end_date and datetime.datetime.strptime(end_date, "%Y-%m-%d").date()

    return end_date


def is_renewable_contribution(contribution):
    renewal_start = (
        timezone.now()
        + relativedelta(months=settings.CONTRIBUTION_MONTHS_BEFORE_END_RENEWAL_START)
    ).date()

    end_date = get_contribution_end_date(contribution)

    if not end_date:
        return False

    return end_date <= renewal_start


def is_waiting_contribution(contribution):
    return (
        isinstance(contribution, Payment)
        and contribution.status == Payment.STATUS_WAITING
    )


def can_make_contribution(email=None, person=None):
    if not email and not person:
        return False

    if not person:
        try:
            person = Person.objects.get_by_natural_key(email)
        except Person.DoesNotExist:
            return True

    active_contribution = get_active_contribution_for_person(person)

    return active_contribution is None or is_renewable_contribution(active_contribution)
