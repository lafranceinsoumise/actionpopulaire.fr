from django.conf import settings
from django.db.models import Sum

from agir.donations.apps import DonsConfig
from agir.donations.models import Operation, MonthlyAllocation
from agir.payments.actions.subscriptions import create_subscription


def get_balance(group):
    return (
        Operation.objects.filter(group=group).aggregate(sum=Sum("amount"))["sum"] or 0
    )


def group_can_handle_allocation(group):
    return group.subtypes.filter(label__in=settings.CERTIFIED_GROUP_SUBTYPES).exists()


def create_monthly_allocation(
    person, mode, subscription_total, group=None, allocation_amount=0, **kwargs
):
    subscription = create_subscription(
        person=person,
        price=subscription_total,
        mode=mode,
        type=DonsConfig.SUBSCRIPTION_TYPE,
        day_of_month=settings.MONTHLY_DONATION_DAY,
        **kwargs
    )

    allocation = None
    if group is not None:
        allocation = MonthlyAllocation.objects.create(
            subscription=subscription, group=group, amount=allocation_amount
        )

    return subscription, allocation
