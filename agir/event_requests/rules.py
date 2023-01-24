import rules

from agir.lib.rules import is_authenticated_person
from .models import EventSpeaker, EventSpeakerRequest, EventRequest


@rules.predicate
def is_own_person(role, obj=None):
    if obj is None:
        return False

    if isinstance(obj, EventSpeaker):
        return role.person.id == obj.person_id

    if isinstance(obj, EventSpeakerRequest):
        return role.person.id == obj.event_speaker.person_id

    return False


@rules.predicate
def is_answerable_speaker_request(_, obj=None):
    if obj is None:
        return False

    if isinstance(obj, EventSpeakerRequest):
        return obj.is_answerable

    return False


# EventSpeaker
rules.add_perm(
    "event_requests.view_event_speaker",
    is_authenticated_person & is_own_person,
)
rules.add_perm(
    "event_requests.change_event_speaker",
    is_authenticated_person & is_own_person,
)
# EventSpeakerRequest
rules.add_perm(
    "event_requests.view_event_speaker_request",
    is_authenticated_person & is_own_person,
)
rules.add_perm(
    "event_requests.change_event_speaker_request",
    is_authenticated_person & is_own_person & is_answerable_speaker_request,
)
