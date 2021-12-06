import rules

from agir.msgs.models import SupportGroupMessage
from agir.groups.models import Membership
from ..groups.rules import is_at_least_manager_for_group, is_group_member


@rules.predicate
def is_authenticated_person(role):
    return role.is_authenticated and hasattr(role, "person")


@rules.predicate
def is_own_organization_message(role, message=None):

    if message is None:
        return False

    if not isinstance(message, SupportGroupMessage):
        return False

    supportgroup = message.supportgroup
    if supportgroup is None:
        return False

    if message.required_membership_type <= Membership.MEMBERSHIP_TYPE_FOLLOWER:
        return False

    # Is author
    if message.author.pk == role.person.pk:
        return True

    # Is in required roles
    return supportgroup.memberships.filter(
        person_id=role.person.pk, membership_type__gte=message.required_membership_type
    ).exists()


@rules.predicate
def is_organization_message(role, message=None):
    if message is None:
        return False

    if not isinstance(message, SupportGroupMessage):
        return False

    supportgroup = message.supportgroup
    if supportgroup is None:
        return False

    return message.required_membership_type > Membership.MEMBERSHIP_TYPE_FOLLOWER


@rules.predicate
def is_msg_author(role, msg=None):
    return msg is not None and msg.author == role.person


rules.add_perm(
    "msgs.view_supportgroupmessage",
    is_authenticated_person
    & (is_own_organization_message | (~is_organization_message & is_group_member)),
)
rules.add_perm(
    "msgs.add_supportgroupmessage",
    is_authenticated_person & is_at_least_manager_for_group,
)
rules.add_perm(
    "msgs.change_supportgroupmessage", is_authenticated_person & is_msg_author
)
rules.add_perm(
    "msgs.delete_supportgroupmessage",
    is_authenticated_person & (is_msg_author | is_at_least_manager_for_group),
)
rules.add_perm(
    "msgs.add_supportgroupmessagecomment",
    is_authenticated_person
    & (is_own_organization_message | (~is_organization_message & is_group_member)),
)
rules.add_perm(
    "msgs.change_supportgroupmessagecomment", is_authenticated_person & is_msg_author
)
rules.add_perm(
    "msgs.delete_supportgroupmessagecomment",
    is_authenticated_person & (is_msg_author | is_at_least_manager_for_group),
)
