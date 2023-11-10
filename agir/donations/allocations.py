import json

from django.db import transaction
from django.db.models import Sum

from agir.donations.models import (
    MonthlyAllocation,
    AllocationModelMixin,
    AccountOperation,
)
from agir.groups.models import SupportGroup
from agir.lib.data import departements_choices

DONATIONS_ACCOUNT = "revenu:dons"
COTISATIONS_ACCOUNT = "revenu:cotisations"
CNS_ACCOUNT = "actif:cns"
SPENDING_ACCOUNT = "depenses"


def get_account_name_for_departement(departement):
    departement = departement.zfill(2)
    return f"actif:departement:{departement}"


def get_account_name_for_group(group):
    group_id = group.id if isinstance(group, SupportGroup) else group
    return f"actif:groupe:{group_id}"


def get_account_balance(account: str):
    incomes = (
        AccountOperation.objects.filter(destination=account).aggregate(
            sum=Sum("amount")
        )["sum"]
        or 0
    )
    outcomes = (
        AccountOperation.objects.filter(source=account).aggregate(sum=Sum("amount"))[
            "sum"
        ]
        or 0
    )
    return incomes - outcomes


def get_balance(qs):
    return qs.aggregate(sum=Sum("amount"))["sum"] or 0


def get_supportgroup_balance(group):
    return get_account_balance(get_account_name_for_group(group))


def get_departement_balance(departement):
    return get_account_balance(get_account_name_for_departement(departement))


def get_cns_balance():
    return get_account_balance(CNS_ACCOUNT)


def get_allocation_list(allocations, limit_to_type=None, with_labels=False):
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

    if with_labels:
        for allocation in allocation_list:
            allocation["label"] = dict(AllocationModelMixin.TYPE_CHOICES).get(
                allocation.get("type")
            )

            if allocation.get("group"):
                allocation["group"] = (
                    SupportGroup.objects.filter(pk=allocation["group"]).first()
                    or allocation["group"]
                )

            if allocation.get("departement"):
                allocation["departement"] = (
                    dict(departements_choices).get(allocation.get("departement"))
                    or allocation["departement"]
                )

    return allocation_list


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
        AccountOperation.objects.update_or_create(
            payment=payment,
            source=DONATIONS_ACCOUNT,
            destination=get_account_name_for_group(group),
            defaults={"amount": allocation["amount"]},
        )
    elif allocation_type == AllocationModelMixin.TYPE_DEPARTEMENT:
        AccountOperation.objects.update_or_create(
            payment=payment,
            source=DONATIONS_ACCOUNT,
            destination=get_account_name_for_departement(allocation["departement"]),
            defaults={"amount": allocation["amount"]},
        )
    elif allocation_type == AllocationModelMixin.TYPE_CNS:
        AccountOperation.objects.update_or_create(
            payment=payment,
            source=DONATIONS_ACCOUNT,
            destination=CNS_ACCOUNT,
            defaults={"amount": allocation["amount"]},
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


def cancel_payment_allocations(payment):
    with transaction.atomic():
        for operation in payment.account_operations.all():
            AccountOperation.objects.create(
                source=operation.destination,
                destination=operation.source,
                amount=operation.amount,
                comment=f"Annule l'opération #{operation.id} ({str(payment)})",
            )


def create_spending_for_group(*, group, amount):
    return AccountOperation.objects.create(
        amount=amount,
        source=get_account_name_for_group(group),
        destination=SPENDING_ACCOUNT,
    )
