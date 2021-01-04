import rules

from . import models


@rules.predicate
def is_person(role, obj):
    return (
        obj
        and role.is_authenticated
        and role.type == role.PERSON_ROLE
        and role.person == obj
    )


rules.add_perm("people.view_person", is_person)
rules.add_perm("people.change_person", is_person)
