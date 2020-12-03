import rules

from ..lib.rules import is_authenticated_person


@rules.predicate
def is_own_activity(role, activity=None):
    return activity is not None and role.person == activity.recipient


rules.add_perm("activity.view_activity", is_authenticated_person & is_own_activity)
rules.add_perm("activity.change_activity", is_authenticated_person & is_own_activity)
