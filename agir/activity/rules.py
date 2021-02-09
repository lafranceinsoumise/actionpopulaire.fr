import rules

from ..lib.rules import is_authenticated_person


@rules.predicate
def is_own_activity(role, activity=None):
    return activity is not None and role.person == activity.recipient


@rules.predicate
def can_view_linked_object(role, activity=None):
    if activity is None:
        return False

    if activity.event is not None and not role.has_perm(
        "events.view_event", activity.event
    ):
        return False

    if activity.supportgroup is not None and not role.has_perm(
        "groups.view_supportgroup", activity.supportgroup
    ):
        return False

    return True


rules.add_perm(
    "activity.view_activity",
    is_authenticated_person & is_own_activity & can_view_linked_object,
)
rules.add_perm("activity.change_activity", is_authenticated_person & is_own_activity)
