import rules

from authentication.models import Role

@rules.predicate
def is_organizer(role, event=None):
    return (
        event is not None and
        role.is_authenticated and
        role.type == Role.PERSON_ROLE and
        role.person.organized_events.filter(pk=event.pk).exists()
    )


rules.add_perm('events.change_event', is_organizer)
