import rules

from agir.msgs.models import SupportGroupMessage


@rules.predicate
def is_authenticated_person(role):
    return role.is_authenticated and hasattr(role, "person")


@rules.predicate
def is_own_group_message(role, message=None):
    if message is None:
        return False

    if message.message_type == SupportGroupMessage.MESSAGE_TYPE_ORGANIZATION:
        return False

    if isinstance(message, SupportGroupMessage):
        supportgroup = message.supportgroup
    else:
        return False

    return (
        supportgroup is not None
        and supportgroup.members.filter(pk=role.person.pk).exists()
    )


@rules.predicate
def is_own_organization_message(role, message=None):
    if message is None:
        return False

    if isinstance(message, SupportGroupMessage):
        supportgroup = message.supportgroup
    else:
        return False

    if supportgroup is None:
        return False

    if message.message_type != SupportGroupMessage.MESSAGE_TYPE_ORGANIZATION:
        return False

    # Is author
    if message.author.pk == role.person.pk:
        return True

    # Is in required roles
    is_valid_membership = supportgroup.memberships.filter(
        pk=role.person.pk, membership_type__gte=message.required_membership_type
    ).exists()
    return is_valid_membership


rules.add_perm(
    "msgs.view_message",
    is_authenticated_person & (is_own_organization_message | is_own_group_message),
)
