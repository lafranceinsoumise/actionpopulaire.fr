import rules

from agir.events.models import Event
from ..authentication.models import Role


@rules.predicate
def is_person(role, event=None):
    return role.is_authenticated and role.type == Role.PERSON_ROLE


rules.add_perm("events.add_event", is_person)


@rules.predicate
def is_not_hidden(role, event=None):
    return event is not None and event.visibility != Event.VISIBILITY_ADMIN


@rules.predicate
def is_public(role, event=None):
    return event is not None and event.visibility == Event.VISIBILITY_PUBLIC


@rules.predicate
def is_organizer(role, event=None):
    return (
        event is not None
        and role.is_authenticated
        and role.type == Role.PERSON_ROLE
        and role.person.organized_events.filter(pk=event.pk).exists()
    )


rules.add_perm("events.view_event", is_not_hidden & (is_public | is_organizer))
rules.add_perm("events.change_event", is_not_hidden & is_organizer)


@rules.predicate
def is_own_rsvp(role, rsvp=None):
    return (
        rsvp is not None
        and role.is_authenticated
        and role.type == Role.PERSON_ROLE
        and role.person == rsvp.person
    )


rules.add_perm("events.change_rsvp", is_own_rsvp)


@rules.predicate
def has_rsvp(role, event=None):
    return (
        event is not None
        and role.is_authenticated
        and role.type == Role.PERSON_ROLE
        and role.person.rsvps.filter(event=event).exists()
    )


rules.add_perm("events.view_jitsi_meeting", has_rsvp)
