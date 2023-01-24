import rules

from agir.lib.rules import is_authenticated_person
from .models import EventSpeaker, EventSpeakerRequest, EventRequest


@rules.predicate
def is_own_person(role, object=None):
    if object is None:
        return False

    if isinstance(object, EventSpeaker):
        return role.person.id == object.person_id

    if isinstance(object, EventSpeakerRequest):
        return role.person.id == object.event_speaker.person_id

    return False


@rules.predicate
def is_pending_event_request(role, object=None):
    if object is None:
        return False

    if isinstance(object, EventRequest):
        return object.status == EventRequest.Status.PENDING

    if isinstance(object, EventSpeakerRequest):
        return object.event_request.status == EventRequest.Status.PENDING

    return False


@rules.predicate
def is_answerable_speaker_request(role, object=None):
    if object is None:
        return False

    if isinstance(object, EventSpeakerRequest):
        return object.is_answerable

    return False


rules.add_perm(
    "event_requests.view_event_speaker",
    is_authenticated_person & is_own_person,
)
rules.add_perm(
    "event_requests.update_event_speaker",
    is_authenticated_person & is_own_person,
)
rules.add_perm(
    "event_requests.update_event_speaker_request",
    is_authenticated_person & is_own_person & is_answerable_speaker_request,
)
