import rules

from ..authentication.models import Role


@rules.predicate
def is_person(role, event=None):
    return role.is_authenticated and role.type == Role.PERSON_ROLE


rules.add_perm("events.add_event", is_person)


@rules.predicate
def is_organizer(role, event=None):
    return (
        event is not None
        and role.is_authenticated
        and role.type == Role.PERSON_ROLE
        and role.person.organized_events.filter(pk=event.pk).exists()
    )


rules.add_perm("events.change_event", is_organizer)


@rules.predicate
def is_own_rsvp(role, rsvp=None):
    return (
        rsvp is not None
        and role.is_authenticated
        and role.type == Role.PERSON_ROLE
        and role.person == rsvp.person
    )


@rules.predicate
def is_event_rsvp(role, rsvp=None):
    return rsvp is not None and is_organizer(role, rsvp.event)


rules.add_perm("events.change_rsvp", is_own_rsvp)
