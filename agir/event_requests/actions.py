import datetime
from copy import deepcopy

import pytz
from django.db import transaction, IntegrityError
from django.utils import timezone
from django.utils.text import slugify

from agir.event_requests.models import EventRequest
from agir.events.models import Event, Calendar
from agir.events.tasks import (
    send_event_creation_notification,
    geocode_event,
)
from agir.groups.models import SupportGroup
from agir.groups.tasks import notify_new_group_event, send_new_group_event_email
from agir.people.models import Person


def create_calendar_for_object(obj):
    if not hasattr(obj, "calendar"):
        return

    if hasattr(obj, "event_theme_type"):
        parent_id = obj.event_theme_type.calendar_id
        name = f"{obj.name} ({obj.event_theme_type.name})"
        slug = slugify(f"{obj.event_theme_type.calendar.slug}-{obj.name}")
    else:
        parent_id = None
        name = obj.name
        slug = slugify(f"e-{obj.name}")

    calendar, _ = Calendar.objects.get_or_create(
        slug=slug,
        defaults={
            "name": name,
            "user_contributed": False,
            "parent_id": parent_id,
            "archived": True,
        },
    )

    obj.calendar_id = calendar.id
    obj.save()


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

    data = {
        k: v for k, v in data.items() if k in [f.name for f in Event._meta.get_fields()]
    }

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

    if event_request.event_theme.event_theme_type.calendar:
        event_request.event_theme.event_theme_type.calendar.events.add(event)

    if event_request.event_theme.calendar:
        event_request.event_theme.calendar.events.add(event)

    schedule_new_event_tasks(event)

    return event


def create_event_request_from_personform_submission(submission, do_not_create=False):
    submission_data = deepcopy(submission.data)
    event_data = {
        "from_personform": submission.form_id,
        "from_personform_submission_id": submission.id,
        "organizer_person_id": submission_data.pop(
            "organizer_person_id", str(submission.person_id)
        ),
        "contact_hide_phone": submission_data.pop("contact_hide_phone", True),
        **submission_data,
    }
    event_request_data = {
        "datetimes": event_data.pop("datetimes", None),
        "event_theme_id": event_data.pop("event_theme", None),
        "location_zip": event_data.pop("location_zip", None),
        "location_city": event_data.pop("location_city", None),
        "location_country": event_data.pop("location_country", None),
        "comment": event_data.pop("comment", ""),
        "event_data": event_data,
    }
    if do_not_create:
        return EventRequest(**event_request_data)

    with transaction.atomic():
        event_request = EventRequest.objects.create(**event_request_data)
        submission.data["event_request_id"] = event_request.id
        submission.save()

        return event_request
