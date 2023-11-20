import rules

from agir.donations.models import SpendingRequest
from agir.groups.models import SupportGroup
from agir.groups.rules import (
    is_financeable_group,
    is_at_least_manager_for_group,
    is_finance_manager,
)
from agir.lib.rules import is_authenticated_person


@rules.predicate
def is_editable_spending_request(_role, spending_request):
    return spending_request is not None and spending_request.editable


@rules.predicate
def is_deletable_spending_request(_role, spending_request):
    return spending_request is not None and spending_request.deletable


@rules.predicate
def is_finance_manager_of_at_least_one_financeable_group(role):
    for group in role.person.supportgroups.financeable():
        if is_financeable_group(role, group) and is_finance_manager(role, group):
            return True
    return False


@rules.predicate
def is_finance_manager_of_spending_request_group(role, obj=None):
    group = None
    if isinstance(obj, SpendingRequest):
        group = obj.group
    if isinstance(obj, SupportGroup):
        group = obj

    if group is None:
        return False

    return is_financeable_group(role, group) and is_finance_manager(role, group)


@rules.predicate
def is_own_contribution(role, obj=None):
    if obj is None:
        return False
    return obj.person == role.person


rules.add_perm(
    "donations.view_spendingrequest",
    is_authenticated_person & is_finance_manager_of_spending_request_group,
)
rules.add_perm(
    "donations.add_spendingrequest",
    is_authenticated_person & is_financeable_group & is_at_least_manager_for_group,
)
rules.add_perm(
    "donations.change_spendingrequest",
    is_authenticated_person
    & is_editable_spending_request
    & is_finance_manager_of_spending_request_group,
)
rules.add_perm(
    "donations.delete_spendingrequest",
    is_authenticated_person
    & is_deletable_spending_request
    & is_finance_manager_of_spending_request_group,
)
rules.add_perm(
    "donations.add_document_to_spending_request",
    is_authenticated_person & is_finance_manager_of_spending_request_group,
)
rules.add_perm(
    "donations.view_active_contribution", is_authenticated_person & is_own_contribution
)
