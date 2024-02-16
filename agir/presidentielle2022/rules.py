import rules
from django.db.models import F

from agir.groups.models import Membership, SupportGroup


@rules.predicate
def is_authenticated_person(role):
    return role.is_authenticated and hasattr(role, "person")


@rules.predicate
def is_certified_group_manager(role, person):
    if hasattr(person, "certified_groups_with_active_membership"):
        return any(
            group.membership_type >= Membership.MEMBERSHIP_TYPE_MANAGER
            for group in person.certified_groups_with_active_membership
        )

    return (
        SupportGroup.objects.filter(memberships__person_id=person.id)
        .active()
        .certified()
        .annotate(membership_type=F("memberships__membership_type"))
        .filter(membership_type__gte=Membership.MEMBERSHIP_TYPE_MANAGER)
        .exists()
    )


@rules.predicate
def is_group_active_member(role, person):
    if hasattr(person, "groups_with_active_membership"):
        return any(
            group.membership_type >= Membership.MEMBERSHIP_TYPE_MEMBER
            for group in person.groups_with_active_membership
        )

    return (
        SupportGroup.objects.filter(memberships__person_id=person.id)
        .active()
        .annotate(membership_type=F("memberships__membership_type"))
        .filter(membership_type__gte=Membership.MEMBERSHIP_TYPE_MEMBER)
        .exists()
    )


rules.add_perm("toktok.access_data", is_authenticated_person & is_group_active_member)
