from uuid import UUID

from iso8601 import iso8601

from agir.events.models import Event

TREVE_ELECTORALE = [
    # Législatives 2022
    ("2022-06-11 00:00:00+0200", "2022-06-12 20:00:00+0200", ("soiree-electorale",)),
    ("2022-06-18 00:00:00+0200", "2022-06-19 20:00:00+0200", ("soiree-electorale",)),
]
TREVE_ELECTORALE = [
    (iso8601.parse_date(start), iso8601.parse_date(end), *rest)
    for (start, end, *rest) in TREVE_ELECTORALE
]


def is_forbidden_during_treve_event(event):
    if isinstance(event, UUID):
        event = Event.objects.get(pk=event)
    if isinstance(event, dict):
        start_time = event.get("start_time", None)
        end_time = event.get("end_time", None)
        subtype = event.get("subtype", None)
        if not start_time and not end_time and not subtype:
            return False
        event = Event(start_time=start_time, end_time=end_time, subtype=subtype)

    for treve_start, treve_end, authorized_subtype_labels in TREVE_ELECTORALE:
        if (
            hasattr(event, "subtype")
            and event.subtype
            and event.subtype.label in authorized_subtype_labels
        ):
            continue
        if event.start_time is None or event.end_time is None:
            return True
        if (
            treve_start <= event.start_time < treve_end
            or treve_start <= event.end_time < treve_end
        ):
            return True

    return False
