import json

from django.conf import settings
from django.db import transaction
from django.db.models import Sum

from agir.donations.apps import DonsConfig
from agir.donations.models import (
    Operation,
    MonthlyAllocation,
    DepartementOperation,
    CNSOperation,
    AllocationModelMixin,
)
from agir.groups.models import SupportGroup
from agir.payments.actions.subscriptions import create_subscription


def get_balance(qs):
    return qs.aggregate(sum=Sum("amount"))["sum"] or 0


def get_supportgroup_balance(group):
    return get_balance(Operation.objects.filter(group=group))


def get_departement_balance(departement):
    return get_balance(DepartementOperation.objects.filter(departement=departement))


def get_cns_balance():
    return get_balance(CNSOperation.objects.all())


def group_can_handle_allocation(group):
    return group.subtypes.filter(label__in=settings.CERTIFIED_GROUP_SUBTYPES).exists()


def get_allocation_list(allocations, limit_to_type=None):
    allocation_list = allocations

    if isinstance(allocation_list, str):
        try:
            allocation_list = json.loads(allocation_list)
        except ValueError:
            return []

    if isinstance(allocation_list, dict):
        allocation_list = [
            {"type": "group", "group": group, "amount": amount}
            for group, amount in allocation_list.items()
        ]

    if not isinstance(allocation_list, list):
        return []

    if limit_to_type is not None:
        allocation_list = [
            allocation
            for allocation in allocation_list
            if allocation.get("type") == limit_to_type
        ]

    return allocation_list


def create_monthly_donation(
    person,
    mode,
    subscription_total,
    allocations=None,
    type=DonsConfig.SUBSCRIPTION_TYPE,
    **kwargs
):
    subscription = create_subscription(
        person=person,
        price=subscription_total,
        mode=mode,
        type=type,
        day_of_month=settings.MONTHLY_DONATION_DAY,
        **kwargs,
    )

    if allocations is None:
        return subscription

    for allocation in get_allocation_list(allocations):
        group = allocation.pop("group", None)

        if group and not isinstance(group, SupportGroup):
            group = SupportGroup.objects.filter(pk=group).first()

        MonthlyAllocation.objects.create(
            **allocation,
            subscription=subscription,
            group=group,
        )

    return subscription


def apply_payment_allocation(payment, allocation):
    if isinstance(allocation, MonthlyAllocation):
        allocation = allocation.to_dict()

    allocation_type = allocation.get("type")

    if allocation_type == AllocationModelMixin.TYPE_GROUP:
        group = allocation.get("group")
        if not isinstance(group, SupportGroup):
            try:
                group = SupportGroup.objects.get(pk=group)
            except SupportGroup.DoesNotExist:
                return
        Operation.objects.update_or_create(
            payment=payment,
            group=group,
            defaults={"amount": allocation.get("amount")},
        )
    elif allocation_type == AllocationModelMixin.TYPE_DEPARTEMENT:
        DepartementOperation.objects.update_or_create(
            payment=payment,
            departement=allocation.get("departement"),
            defaults={"amount": allocation.get("amount")},
        )
    elif allocation_type == AllocationModelMixin.TYPE_CNS:
        CNSOperation.objects.update_or_create(
            payment=payment,
            defaults={"amount": allocation.get("amount")},
        )


def apply_payment_allocations(payment):
    with transaction.atomic():
        # S'il s'agit d'un don ponctuel, le fléchage éventuel des dons est enregistré dans les meta
        # du paiement. Dans le cas d'un don mensuel, les infos d'allocations sont enregistrées sur la souscription.
        if payment.subscription is None:
            allocations = get_allocation_list(payment.meta.get("allocations", []))
        else:
            allocations = payment.subscription.allocations.all()

        for allocation in allocations:
            apply_payment_allocation(payment, allocation)
