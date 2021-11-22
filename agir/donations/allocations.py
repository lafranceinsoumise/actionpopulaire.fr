from django.conf import settings
from django.db.models import Sum

from agir.donations.apps import DonsConfig
from agir.donations.models import Operation, MonthlyAllocation
from agir.payments.actions.subscriptions import create_subscription
from agir.groups.models import SupportGroup


def get_balance(group):
    return (
        Operation.objects.filter(group=group).aggregate(sum=Sum("amount"))["sum"] or 0
    )


def group_can_handle_allocation(group):
    return group.subtypes.filter(label__in=settings.CERTIFIED_GROUP_SUBTYPES).exists()


def create_monthly_donation(
    person,
    mode,
    subscription_total,
    allocations=None,
    type=DonsConfig.SUBSCRIPTION_TYPE,
    **kwargs
):
    if allocations is None:
        allocations = {}
    subscription = create_subscription(
        person=person,
        price=subscription_total,
        mode=mode,
        type=type,
        day_of_month=settings.MONTHLY_DONATION_DAY,
        **kwargs
    )

    for group_id, amount in allocations.items():
        try:
            group = SupportGroup.objects.get(pk=group_id)
        except SupportGroup.DoesNotExist:
            continue
        MonthlyAllocation.objects.create(
            subscription=subscription, group=group, amount=amount
        )

    return subscription
