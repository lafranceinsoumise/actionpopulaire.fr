import datetime
from copy import deepcopy

import pytz
from django.utils import timezone

from agir.events.models import Event
from agir.groups.models import SupportGroup
from agir.people.models import Person


def create_event_from_event_speaker_request(event_speaker_request=None):
    event_request = event_speaker_request.event_request
    event_date = event_speaker_request.date
    data = deepcopy(event_speaker_request.event_request.event_data)

    organizer_person = None
    organizer_group = None

    if "organizer_person_id" in data:
        organizer_person = Person.objects.filter(
            pk=data.pop("organizer_person_id")
        ).first()

    if "organizer_group_id" in data:
        organizer_group = (
            SupportGroup.objects.active()
            .filter(pk=data.pop("organizer_group_id"))
            .first()
        )

    subtype = event_request.event_theme.event_theme_type.event_subtype

    tz = data.pop("timezone", None)
    if tz not in pytz.all_timezones:
        tz = timezone.get_default_timezone().zone

    start_time = datetime.time.fromisoformat(
        data.pop("start_time", str(datetime.time.min))
    )
    start_time = datetime.datetime.combine(
        event_date, start_time, tzinfo=pytz.timezone(tz)
    )

    end_time = datetime.time.fromisoformat(data.pop("end_time", str(datetime.time.max)))
    end_time = datetime.datetime.combine(event_date, end_time, tzinfo=pytz.timezone(tz))

    data["location_zip"] = event_request.location_zip
    data["location_city"] = event_request.location_city
    data["location_country"] = str(event_request.location_country)

    data["name"] = (
        f"{event_request.event_theme.event_theme_type.name} "
        f"sur le thème '{event_request.event_theme.name}' "
        f"avec {event_speaker_request.event_speaker.person.get_full_name()}"
    )

    event = Event.objects.create_event(
        visibility=Event.VISIBILITY_PUBLIC,
        organizer_person=organizer_person,
        organizer_group=organizer_group,
        start_time=start_time,
        end_time=end_time,
        timezone=tz,
        subtype=subtype,
        description=data.pop("description", subtype.default_description),
        image=data.pop("image", subtype.default_image),
        **data,
    )

    return event
