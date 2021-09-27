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


@rules.predicate
def is_a_person(role):
    return role.is_authenticated and role.person is not None


rules.add_perm("people.view_person", is_person)
rules.add_perm("people.change_person", is_person)
rules.add_perm("people.create_contact", is_a_person)
