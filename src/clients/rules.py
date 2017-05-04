import rules

from . import models


@rules.predicate
def is_client(role, obj):
    return obj and role.type == role.CLIENT_ROLE and role.client == obj


rules.add_perm('clients.view_client', is_client)
rules.add_perm('clients.change_client', is_client)
