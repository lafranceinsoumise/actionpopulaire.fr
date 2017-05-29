import rules
from django.db.models import Q

from authentication.models import Role
from .models import Membership


@rules.predicate
def is_referent_or_manager(role, supportgroup=None):
    return (
        supportgroup is not None and
        role.is_authenticated and
        role.type == Role.PERSON_ROLE and
        Membership.objects.filter(Q(is_manager=True) | Q(is_referent=True), person=role.person, supportgroup=supportgroup).exists()
    )


rules.add_perm('groups.change_supportgroup', is_referent_or_manager)


@rules.predicate
def is_own_membership(role, membership=None):
    return (
        membership is not None and
        role.is_authenticated and
        role.type == Role.PERSON_ROLE and
        role.person == membership.person
    )


@rules.predicate
def is_group_referent_or_manager(role, membership=None):
    return (
        membership is not None and is_referent_or_manager(role, membership.supportgroup)
    )


rules.add_perm('groups.change_membership', is_own_membership | is_group_referent_or_manager)
