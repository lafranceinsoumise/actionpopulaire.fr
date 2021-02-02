import rules

from agir.authentication.models import Role
from agir.lib.rules import is_authenticated_person
from .models import Membership, SupportGroup
from ..msgs.models import SupportGroupMessage, SupportGroupMessageComment


@rules.predicate
def is_group_published(role, supportgroup=None):
    return supportgroup is not None and supportgroup.published


@rules.predicate
def is_at_least_manager_for_group(role, object=None):
    if object is None:
        return False

    if isinstance(object, SupportGroup):
        supportgroup = object
    elif isinstance(object, SupportGroupMessage):
        supportgroup = object.supportgroup
    elif isinstance(object, SupportGroupMessageComment):
        supportgroup = object.message.supportgroup
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
def is_at_least_referent_for_group(role, supportgroup=None):
    return supportgroup is not None and Membership.objects.filter(
        membership_type__gte=Membership.MEMBERSHIP_TYPE_REFERENT,
        person=role.person,
        supportgroup=supportgroup,
    )


@rules.predicate
def is_group_only_referent(role, object=None):
    if object is None:
        return False

    if isinstance(object, Membership):
        membership = object
    else:
        membership = object.memberships.filter(person=role.person).first()

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
def is_group_member(role, object=None):
    if object is None:
        return False

    if isinstance(object, SupportGroup):
        supportgroup = object
    elif isinstance(object, SupportGroupMessage):
        supportgroup = object.supportgroup
    else:
        return False

    return (
        supportgroup is not None
        and supportgroup.members.filter(pk=role.person.pk).exists()
    )


@rules.predicate
def is_msg_author(role, msg=None):
    return msg is not None and msg.author == role.person


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
rules.add_perm(
    "groups.transfer_members", is_authenticated_person & is_at_least_manager_for_group
)
rules.add_perm("msgs.view_supportgroupmessage", is_group_member)
rules.add_perm("msgs.add_supportgroupmessage", is_at_least_manager_for_group)
rules.add_perm("msgs.change_supportgroupmessage", is_msg_author)
rules.add_perm("msgs.delete_supportgroupmessage", is_msg_author)
rules.add_perm("msgs.add_supportgroupmessagecomment", is_group_member)
rules.add_perm("msgs.change_supportgroupmessagecomment", is_msg_author)
rules.add_perm(
    "msgs.delete_supportgroupmessagecomment",
    is_msg_author | is_at_least_manager_for_group,
)
