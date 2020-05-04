import rules

from agir.authentication.models import Role
from agir.lib.rules import is_authenticated_person
from .models import Membership


@rules.predicate
def is_group_published(role, supportgroup=None):
    return supportgroup is not None and supportgroup.published


@rules.predicate
def is_at_least_manager_for_group(role, supportgroup=None):
    return (
        supportgroup is not None
        and Membership.objects.filter(
            membership_type__gte=Membership.MEMBERSHIP_TYPE_MANAGER,
            person=role.person,
            supportgroup=supportgroup,
        ).exists()
    )


@rules.predicate
def is_at_least_referent_for_group(role, supportgroup=None):
    return supportgroup is not None and Membership.objects.filter(
        membership_type__gte=Membership.MEMBERSHIP_TYPE_REFERENT,
        person=role.person,
        supportgroup=supportgroup,
    )


@rules.predicate
def is_group_only_referent(role, membership_or_group=None):
    if membership_or_group is None:
        return False

    if isinstance(membership_or_group, Membership):
        membership = membership_or_group
    else:
        membership = membership_or_group.memberships.filter(person=role.person).first()

    return (
        membership is not None
        and membership.membership_type >= Membership.MEMBERSHIP_TYPE_REFERENT
        and not Membership.objects.filter(
            supportgroup=membership.supportgroup,
            membership_type__gte=Membership.MEMBERSHIP_TYPE_REFERENT,
        )
        .exclude(id=membership.id)
        .exists()
    )


@rules.predicate
def is_own_membership(role, membership=None):
    return (
        membership is not None
        and role.is_authenticated
        and role.type == Role.PERSON_ROLE
        and role.person == membership.person
    )


@rules.predicate
def own_membership_has_higher_rights(role, membership=None):
    return membership is not None and (
        Membership.objects.filter(
            person=role.person,
            supportgroup=membership.supportgroup,
            membership_type__gt=membership.membership_type,
        ).exists()
    )


rules.add_perm(
    "groups.change_supportgroup",
    is_authenticated_person & is_at_least_manager_for_group,
)
rules.add_perm(
    "groups.spend_group_allocation",
    is_authenticated_person & is_at_least_manager_for_group,
)
rules.add_perm(
    "groups.change_group_name", is_authenticated_person & is_at_least_referent_for_group
)
rules.add_perm(
    "groups.delete_supportgroup",
    is_authenticated_person & is_at_least_referent_for_group,
)
rules.add_perm("groups.view_supportgroup", is_group_published)
rules.add_perm(
    "groups.add_manager_to_supportgroup",
    is_authenticated_person & is_at_least_referent_for_group,
)
rules.add_perm(
    "groups.add_referent_to_supportgroup",
    is_authenticated_person & is_group_only_referent,
)
rules.add_perm(
    "groups.change_membership",
    is_authenticated_person & own_membership_has_higher_rights,
)
rules.add_perm(
    "groups.delete_membership",
    is_authenticated_person & is_own_membership & (~is_group_only_referent),
)
