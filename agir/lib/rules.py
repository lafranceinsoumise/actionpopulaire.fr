import rules


@rules.predicate
def is_authenticated_person(role):
    return role.is_authenticated and hasattr(role, "person")
