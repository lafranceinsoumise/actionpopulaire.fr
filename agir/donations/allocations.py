from django.conf import settings
from django.db.models import Sum

from agir.donations.models import Operation


def get_balance(group):
    return (
        Operation.objects.filter(group=group).aggregate(sum=Sum("amount"))["sum"] or 0
    )


def group_can_handle_allocation(group):
    return group.subtypes.filter(label__in=settings.CERTIFIED_GROUP_SUBTYPES).exists()
