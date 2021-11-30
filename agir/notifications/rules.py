import rules

from ..lib.rules import is_authenticated_person


@rules.predicate
def is_own_subscription(role, subscription=None):
    return subscription is not None and role.person == subscription.person


rules.add_perm("notifications.add_subscription", is_authenticated_person)
rules.add_perm(
    "notifications.view_subscription",
    is_authenticated_person & is_own_subscription,
)
rules.add_perm(
    "notifications.edit_subscription",
    is_authenticated_person & is_own_subscription,
)
rules.add_perm(
    "notifications.delete_subscription",
    is_authenticated_person & is_own_subscription,
)
