import rules

from authentication.models import Role
from .models import Membership


@rules.predicate
def is_referent(role, support_group=None):
    return (
        support_group is not None and
        role.is_authenticated and
        role.type == Role.PERSON_ROLE and
        Membership.objects.filter(person=role.person, support_group=support_group, is_referent=True).exists()
    )


rules.add_perm('groups.change_supportgroup', is_referent)
