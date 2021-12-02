import rules

from agir.msgs.models import SupportGroupMessage


@rules.predicate
def is_authenticated_person(role):
    return role.is_authenticated and hasattr(role, "person")


@rules.predicate
def is_own_group_message(role, message=None):
    if message is None:
        return False

    if isinstance(message, SupportGroupMessage):
        supportgroup = message.supportgroup
    else:
        return False

    return (
        supportgroup is not None
        and supportgroup.members.filter(pk=role.person.pk).exists()
    )


rules.add_perm(
    "msgs.view_message",
    is_authenticated_person & is_own_group_message,
)
