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
        memberships__membership_type__gte=Membership.MEMBERSHIP_TYPE_REFERENT,
    ).exists():
        return True

    return False


@rules.predicate
# From organizers and group organizers of event : get is at least manager
def is_at_least_manager_of_event(role, event=None):
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
def can_rsvp_event(role, event=None):
    return event is not None and event.can_rsvp(role.person)


@rules.predicate
def can_cancel_rsvp_for_event(role, event=None):
    return event is not None and event.can_cancel_rsvp(role.person)


@rules.predicate
def can_cancel_rsvp(_role, rsvp=None):
    return rsvp is not None and rsvp.can_cancel()


@rules.predicate
def can_rsvp_event_as_group(role, event=None):
    return event is not None and event.can_rsvp_as_group(role.person)


@rules.predicate
def is_free_event(role, event=None):
    return event is not None and event.is_free


@rules.predicate
def is_upcoming_event(role, event=None):
    return event is not None and not event.is_past()


@rules.predicate
def is_editable_event(role, event=None):
    return event is not None and event.subtype.is_editable


@rules.predicate
def has_event_with_missing_documents(role):
    organized_event_projects = Projet.objects.filter(
        event__in=role.person.organized_events.exclude(
            subtype__related_project_type=""
        ).exclude(visibility=Event.VISIBILITY_ADMIN)
    )
    return any(get_is_blocking_project(project) for project in organized_event_projects)


@rules.predicate
def can_respond_to_coorganization_invitation(role, invitation):
    if invitation and invitation.person_recipient == role.person:
        return True

    if invitation and invitation.group and role.person in invitation.group.managers:
        return True

    return False


rules.add_perm("events.add_event", is_authenticated_person)
rules.add_perm(
    "events.view_event",
    is_public_event
    | (~is_hidden_event & is_authenticated_person & is_at_least_manager_of_event),
)
rules.add_perm(
    "events.view_event_settings",
    ~is_hidden_event & is_authenticated_person & is_at_least_manager_of_event,
)
rules.add_perm(
    "events.upload_event_documents",
    ~is_hidden_event & is_authenticated_person & is_at_least_manager_of_event,
)
rules.add_perm(
    "events.change_event",
    ~is_hidden_event
    & is_editable_event
    & is_authenticated_person
    & is_at_least_manager_of_event,
)
rules.add_perm(
    "events.delete_event",
    ~is_hidden_event
    & is_editable_event
    & is_authenticated_person
    & is_organizer_of_event,
)

# for RSVP API
rules.add_perm(
    "events.create_rsvp_for_event",
    is_public_event & is_authenticated_person & can_rsvp_event,
)
rules.add_perm(
    "events.cancel_rsvp_for_event",
    is_public_event
    & is_upcoming_event
    & is_authenticated_person
    & can_cancel_rsvp_for_event,
)
rules.add_perm(
    "events.rsvp_event_as_group",
    is_public_event & is_authenticated_person & can_rsvp_event_as_group,
)


rules.add_perm("events.change_rsvp", is_authenticated_person & is_own_rsvp)
rules.add_perm(
    "events.cancel_rsvp", is_authenticated_person & is_own_rsvp & can_cancel_rsvp
)

rules.add_perm("events.participate_online", has_rsvp_for_event)

rules.add_perm(
    "events.respond_to_coorganization_invitation",
    is_authenticated_person & can_respond_to_coorganization_invitation,
)
rules.add_perm(
    "events.upload_image",
    is_public_event
    & is_authenticated_person
    & is_editable_event
    & (has_rsvp_for_event | is_organizer_of_event),
)
