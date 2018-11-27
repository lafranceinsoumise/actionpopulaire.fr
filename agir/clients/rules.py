import rules

from . import models


@rules.predicate
def is_client(role, obj):
    return obj and role.type == role.CLIENT_ROLE and role.client == obj


rules.add_perm("clients.view_client", is_client)
rules.add_perm("clients.change_client", is_client)


@rules.predicate
def is_own_authorization(role, obj):
    return obj and role.type == role.PERSON_ROLE and role.person == obj.person


rules.add_perm("clients.view_authorization", is_own_authorization)
rules.add_perm("clients.change_authorization", is_own_authorization)
rules.add_perm("clients.delete_authorization", is_own_authorization)
