import datetime
from copy import deepcopy

import pytz
from django.utils import timezone

from agir.events.models import Event
from agir.events.tasks import (
    send_event_creation_notification,
    geocode_event,
)
from agir.groups.models import SupportGroup
from agir.groups.tasks import notify_new_group_event, send_new_group_event_email
from agir.people.models import Person


def schedule_new_event_tasks(event):
    organizer_config = event.organizer_configs.first()
    organizer_group = event.organizers_groups.first()

    geocode_event.delay(event.pk)

    if organizer_config:
        send_event_creation_notification.delay(organizer_config.pk)

    if organizer_group:
        notify_new_group_event.delay(organizer_group.pk, event.pk)
        send_new_group_event_email.delay(organizer_group.pk, event.pk)


def create_event_from_event_speaker_request(event_speaker_request=None):
    event_request = event_speaker_request.event_request
    start_time = event_speaker_request.datetime
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

    duration = int(data.pop("duration", 1))
    end_time = start_time + datetime.timedelta(hours=duration)

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

    event.attendees.add(event_speaker_request.event_speaker.person)
    schedule_new_event_tasks(event)

    return event
