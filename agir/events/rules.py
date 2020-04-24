import rules

from agir.events.models import Event
from ..authentication.models import Role
from ..lib.rules import is_authenticated_person


@rules.predicate
def is_hidden_event(role, event=None):
    return event is not None and event.visibility == Event.VISIBILITY_ADMIN


@rules.predicate
def is_public_event(role, event=None):
    return event is not None and event.visibility == Event.VISIBILITY_PUBLIC


@rules.predicate
def is_organizer_of_event(role, event=None):
    return (
        event is not None and role.person.organized_events.filter(pk=event.pk).exists()
    )


@rules.predicate
def is_own_rsvp(role, rsvp=None):
    return (
        rsvp is not None
        and role.is_authenticated
        and role.type == Role.PERSON_ROLE
        and role.person == rsvp.person
    )


@rules.predicate
def has_rsvp_for_event(role, event=None):
    return (
        event is not None
        and role.is_authenticated
        and role.type == Role.PERSON_ROLE
        and role.person.rsvps.filter(event=event).exists()
    )


rules.add_perm("events.add_event", is_authenticated_person)
rules.add_perm(
    "events.view_event",
    is_public_event
    | (~is_hidden_event & is_authenticated_person & is_organizer_of_event),
)
rules.add_perm(
    "events.change_event",
    ~is_hidden_event & is_authenticated_person & is_organizer_of_event,
)
rules.add_perm("events.change_rsvp", is_own_rsvp)
rules.add_perm("events.delete_rsvp", is_own_rsvp)

rules.add_perm("events.participate_online", has_rsvp_for_event)
