import rules

from agir.authentication.models import Role
from agir.lib.rules import is_authenticated_person
from .models import Membership, SupportGroup
from ..msgs.models import SupportGroupMessage, SupportGroupMessageComment


@rules.predicate
def is_published_group(_role, supportgroup=None):
    return supportgroup is not None and supportgroup.published


@rules.predicate
def is_financeable_group(_role, supportgroup=None):
    return supportgroup is not None and supportgroup.is_financeable


@rules.predicate
def is_editable_group(_role, obj=None):
    if obj is None:
        return False
    if isinstance(obj, SupportGroup):
        supportgroup = obj
    elif hasattr(obj, "supportgroup"):
        supportgroup = obj.supportgroup
    elif isinstance(obj, SupportGroupMessageComment):
        supportgroup = obj.message.supportgroup
    else:
        return False

    return supportgroup.editable


@rules.predicate
def is_at_least_manager_for_group(role, obj=None):
    if obj is None:
        return False

    if isinstance(obj, SupportGroup):
        supportgroup = obj
    elif isinstance(obj, SupportGroupMessage):
        supportgroup = obj.supportgroup
    elif isinstance(obj, SupportGroupMessageComment):
        supportgroup = obj.message.supportgroup
    elif isinstance(obj, Membership):
        supportgroup = obj.supportgroup
    else:
        return False

    return (
        supportgroup is not None
        and Membership.objects.filter(
            membership_type__gte=Membership.MEMBERSHIP_TYPE_MANAGER,
            person=role.person,
            supportgroup=supportgroup,
        ).exists()
    )


@rules.predicate
def is_at_least_referent_for_group(role, obj=None):
    if obj is None:
        return False

    if isinstance(obj, SupportGroup):
        supportgroup = obj
    elif isinstance(obj, SupportGroupMessage):
        supportgroup = obj.supportgroup
    elif isinstance(obj, SupportGroupMessageComment):
        supportgroup = obj.message.supportgroup
    elif isinstance(obj, Membership):
        supportgroup = obj.supportgroup
    else:
        return False

    return Membership.objects.filter(
        membership_type__gte=Membership.MEMBERSHIP_TYPE_REFERENT,
        person=role.person,
        supportgroup=supportgroup,
    )


@rules.predicate
def is_finance_manager(role, obj=None):
    if obj is None:
        return False

    if isinstance(obj, Membership):
        return obj.is_finance_manager

    if isinstance(obj, SupportGroup):
        supportgroup = obj
    elif isinstance(obj, SupportGroupMessage):
        supportgroup = obj.supportgroup
    elif isinstance(obj, SupportGroupMessageComment):
        supportgroup = obj.message.supportgroup
    else:
        return False

    return (
        supportgroup.memberships.finance_managers().filter(person__role=role).exists()
    )


@rules.predicate
def is_group_only_referent(role, obj=None):
    if obj is None:
        return False

    if isinstance(obj, Membership):
        membership = obj
    else:
        membership = obj.memberships.filter(person=role.person).first()

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


@rules.predicate
def is_group_member(role, obj=None):
    if obj is None:
        return False
    if isinstance(obj, SupportGroup):
        supportgroup_id = obj.id
    elif isinstance(obj, SupportGroupMessage):
        supportgroup_id = obj.supportgroup_id
    else:
        return False
    return (
        supportgroup_id is not None
        and Membership.objects.filter(
            supportgroup_id=supportgroup_id, person_id=role.person.pk
        ).exists()
    )


rules.add_perm(
    "groups.change_supportgroup",
    is_authenticated_person & is_at_least_manager_for_group,
)
rules.add_perm(
    "groups.change_group_location",
    is_editable_group & is_authenticated_person & is_at_least_manager_for_group,
)
rules.add_perm(
    "groups.change_group_name",
    is_editable_group & is_authenticated_person & is_at_least_referent_for_group,
)
rules.add_perm(
    "groups.delete_supportgroup",
    is_editable_group & is_authenticated_person & is_at_least_referent_for_group,
)
rules.add_perm("groups.view_supportgroup", is_published_group)
rules.add_perm(
    "groups.add_manager_to_supportgroup",
    is_editable_group & is_authenticated_person & is_at_least_referent_for_group,
)
rules.add_perm(
    "groups.add_referent_to_supportgroup",
    is_editable_group & is_authenticated_person & is_group_only_referent,
)
rules.add_perm(
    "groups.change_membership",
    is_editable_group & is_authenticated_person & own_membership_has_higher_rights,
)
rules.add_perm(
    "groups.update_own_membership",
    is_authenticated_person & is_own_membership,
)
rules.add_perm(
    "groups.delete_membership",
    is_authenticated_person & is_own_membership & (~is_group_only_referent),
)
rules.add_perm(
    "groups.download_member_list",
    is_editable_group & is_authenticated_person & is_at_least_manager_for_group,
)
rules.add_perm(
    "groups.download_attendance_list",
    is_authenticated_person & is_at_least_manager_for_group,
)
rules.add_perm(
    "groups.transfer_members",
    is_editable_group & is_authenticated_person & is_at_least_manager_for_group,
)
rules.add_perm(
    "groups.view_member_personal_information",
    is_authenticated_person & is_at_least_manager_for_group,
)
rules.add_perm(
    "groups.change_membership_type",
    is_editable_group & is_authenticated_person & is_at_least_manager_for_group,
)
rules.add_perm(
    "groups.view_group_finance",
    is_authenticated_person & is_at_least_manager_for_group,
)
rules.add_perm(
    "groups.manage_group_finance",
    is_authenticated_person & is_finance_manager,
)
