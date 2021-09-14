import rules

from agir.events.models import Event
from .actions.required_documents import get_is_blocking_project
from ..gestion.models import Projet
from ..groups.models import Membership
from ..lib.rules import is_authenticated_person


@rules.predicate
def is_hidden_event(role, event=None):
    return event is not None and event.visibility == Event.VISIBILITY_ADMIN


@rules.predicate
def is_public_event(role, event=None):
    return event is not None and event.visibility == Event.VISIBILITY_PUBLIC


@rules.predicate
def is_organizer_of_event(role, event=None):
    if event is None:
        return False

    # The person who created the event:
    if role.person.organized_events.filter(pk=event.pk).exists():
        return True

    # All the managers of the groups organizing the event:
    if event.organizers_groups.filter(
        memberships__person=role.person,
        memberships__membership_type__gte=Membership.MEMBERSHIP_TYPE_MANAGER,
    ).exists():
        return True

    return False


@rules.predicate
def is_own_rsvp(role, rsvp=None):
    return rsvp is not None and role.person == rsvp.person


@rules.predicate
def has_rsvp_for_event(role, event=None):
    return event is not None and role.person.rsvps.filter(event=event).exists()


@rules.predicate
def has_right_subscription(role, event=None):
    return event is not None and event.can_rsvp(role.person)


@rules.predicate
def is_free_event(role, event=None):
    return event is not None and event.is_free


@rules.predicate
def has_event_with_missing_documents(role):
    organized_event_projects = Projet.objects.filter(
        event__in=role.person.organized_events.select_related("subtype").filter(
            subtype__related_project_type__isnull=False
        )
    )
    return any(get_is_blocking_project(project) for project in organized_event_projects)


rules.add_perm(
    "events.add_event", is_authenticated_person & ~has_event_with_missing_documents
)
rules.add_perm(
    "events.view_event",
    is_public_event
    | (~is_hidden_event & is_authenticated_person & is_organizer_of_event),
)
rules.add_perm(
    "events.change_event",
    ~is_hidden_event & is_authenticated_person & is_organizer_of_event,
)

# for RSVP API
rules.add_perm(
    "events.create_rsvp_for_event",
    is_public_event & is_authenticated_person & has_right_subscription,
)
rules.add_perm(
    "events.delete_rsvp_for_event",
    is_public_event & is_free_event & is_authenticated_person,
)


rules.add_perm("events.change_rsvp", is_authenticated_person & is_own_rsvp)

rules.add_perm("events.participate_online", has_rsvp_for_event)
