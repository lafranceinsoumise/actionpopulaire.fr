import rules

from agir.donations.spending_requests import can_edit, can_delete
from agir.groups.rules import is_at_least_manager_for_group
from agir.lib.rules import is_authenticated_person


@rules.predicate
def is_editable_spending_request(role, spending_request):
    return spending_request is not None and can_edit(spending_request)


@rules.predicate
def is_deletable_spending_request(role, spending_request):
    return spending_request is not None and can_delete(spending_request)


@rules.predicate
def has_managing_rights_on_group_of_spending_request(role, spending_request):
    return spending_request is not None and is_at_least_manager_for_group(
        role, spending_request.group
    )


rules.add_perm(
    "donations.view_spendingrequest",
    is_authenticated_person & has_managing_rights_on_group_of_spending_request,
)
rules.add_perm(
    "donations.add_spendingrequest",
    is_authenticated_person & is_at_least_manager_for_group,
)
rules.add_perm(
    "donations.change_spendingrequest",
    is_editable_spending_request
    & is_authenticated_person
    & has_managing_rights_on_group_of_spending_request,
)
rules.add_perm(
    "donations.delete_spendingrequest",
    is_deletable_spending_request
    & is_authenticated_person
    & has_managing_rights_on_group_of_spending_request,
)
