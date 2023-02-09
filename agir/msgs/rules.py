import rules

from agir.msgs.models import SupportGroupMessage
from agir.groups.models import Membership
from ..groups.rules import is_at_least_manager_for_group, is_group_member


@rules.predicate
def is_authenticated_person(role):
    return role.is_authenticated and hasattr(role, "person")


@rules.predicate
def can_view_message(role, message=None):
    if not isinstance(message, SupportGroupMessage):
        return False

    if message.supportgroup_id is None:
        return False

    # Is author
    if message.author_id == role.person.id:
        return True

    # Is member and has the right membership_type
    return Membership.objects.filter(
        supportgroup_id=message.supportgroup_id,
        person_id=role.person.id,
        membership_type__gte=message.required_membership_type,
    ).exists()


@rules.predicate
def is_locked_message(role, message=None):
    if not isinstance(message, SupportGroupMessage):
        return False
    return message.is_locked


@rules.predicate
def is_readonly_message(role, message=None):
    if not isinstance(message, SupportGroupMessage):
        return False
    return message.readonly


@rules.predicate
def is_msg_author(role, msg=None):
    return msg is not None and msg.author_id == role.person.id


rules.add_perm(
    "msgs.view_supportgroupmessages", is_authenticated_person & is_group_member
)
rules.add_perm(
    "msgs.view_supportgroupmessage", is_authenticated_person & can_view_message
)
rules.add_perm(
    "msgs.add_supportgroupmessage",
    is_authenticated_person & is_at_least_manager_for_group,
)
rules.add_perm(
    "msgs.change_supportgroupmessage",
    is_authenticated_person & is_msg_author & ~is_readonly_message,
)
rules.add_perm(
    "msgs.delete_supportgroupmessage",
    is_authenticated_person
    & (is_msg_author | is_at_least_manager_for_group)
    & ~is_readonly_message,
)
rules.add_perm(
    "msgs.add_supportgroupmessagecomment",
    is_authenticated_person
    & can_view_message
    & ~is_locked_message
    & ~is_readonly_message,
)
rules.add_perm(
    "msgs.change_supportgroupmessagecomment", is_authenticated_person & is_msg_author
)
rules.add_perm(
    "msgs.delete_supportgroupmessagecomment",
    is_authenticated_person & (is_msg_author | is_at_least_manager_for_group),
)
