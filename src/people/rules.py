import rules

from . import models


@rules.predicate
def is_person(role, obj):
    return obj and hasattr(role, 'person') and role.person == obj


rules.add_perm('people.view_person', is_person)
rules.add_perm('people.change_person', is_person)
