import datetime
from copy import deepcopy
from functools import partial

import pytz
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from agir.event_requests.models import EventRequest, EventAsset, EventSpeakerRequest
from agir.event_requests.tasks import (
    send_event_request_validation_emails,
    send_new_publish_event_asset_notification,
    render_event_assets,
)
from agir.events.models import Calendar
from agir.events.models import Event
from agir.events.tasks import (
    send_event_creation_notification,
    geocode_event,
)
from agir.groups.models import SupportGroup
from agir.groups.tasks import notify_new_group_event, send_new_group_event_email
from agir.people.models import Person


class EventRequestValidationError(Exception):
    pass


class EventSpeakerRequestValidationError(Exception):
    pass


def create_calendar_for_object(obj, save=True):
    if not hasattr(obj, "calendar"):
        return

    if hasattr(obj, "event_theme_type"):
        parent_id = obj.event_theme_type.calendar_id
        name = f"{obj.name} ({obj.event_theme_type.name})"
        slug = slugify(f"e-{obj.event_theme_type.id}-{obj.name}")[:50]
    else:
        parent_id = None
        name = obj.name
        slug = slugify(f"e-{obj.name}")[:50]

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

    if save:
        obj.save()


def schedule_new_event_tasks(event_request):
    event = event_request.event
    organizer_config = event.organizer_configs.only("pk").first()
    organizer_group = event.organizers_groups.only("pk").first()

    geocode_event.delay(event.pk)

    if organizer_config:
        send_event_creation_notification.delay(organizer_config.pk)

    if organizer_group:
        notify_new_group_event.delay(organizer_group.pk, event.pk)
        send_new_group_event_email.delay(organizer_group.pk, event.pk)

    send_event_request_validation_emails.delay(event_request.pk)
    render_event_assets.delay(str(event.pk))


def create_event_for_event_request(event_request, event_speakers, start_time):
    event_theme = event_request.event_theme
    event_theme_type = event_theme.event_theme_type
    event_subtype = event_theme_type.event_subtype

    data = deepcopy(event_request.event_data)

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

    tz = data.pop("timezone", None)
    if tz not in pytz.all_timezones:
        tz = timezone.get_default_timezone().zone

    duration = int(data.pop("duration", 1))
    end_time = start_time + datetime.timedelta(hours=duration)

    data["location_zip"] = event_request.location_zip
    data["location_city"] = event_request.location_city
    data["location_country"] = str(event_request.location_country)

    data["name"] = f"{event_theme_type.name} sur le thème “{event_theme.name}”"
    data["meta"] = {
        "event_theme": event_theme.name,
        "event_theme_type": event_theme_type.name,
    }

    data = {
        k: v for k, v in data.items() if k in [f.name for f in Event._meta.get_fields()]
    }

    event = Event.objects.create(
        visibility=Event.VISIBILITY_PUBLIC,
        organizer_person=organizer_person,
        organizer_group=organizer_group,
        event_speakers=event_speakers,
        start_time=start_time,
        end_time=end_time,
        timezone=tz,
        subtype=event_subtype,
        **data,
    )

    if event_theme_type.calendar:
        event_theme_type.calendar.events.add(event)

    if event_theme.calendar:
        event_theme.calendar.events.add(event)

    if event_image_template_id := event_theme.get_event_image_template_id():
        EventAsset.objects.create(
            render_after_creation=False,
            template_id=event_image_template_id,
            event=event,
            extra_data=event.meta,
            is_event_image=True,
        )

    for event_asset_template_id in event_theme.get_event_asset_template_ids():
        EventAsset.objects.create(
            render_after_creation=True,
            template_id=event_asset_template_id,
            event=event,
            extra_data=event.meta,
        )

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


def create_event_speaker_requests_for_event_request(event_request, commit=True):
    possible_event_speaker_ids = set(
        event_request.event_theme.event_speakers.available().values_list(
            "id", flat=True
        )
    )
    if len(possible_event_speaker_ids) == 0:
        return []

    event_speaker_requests = []
    for dt in event_request.datetimes:
        existing_speaker_ids = set(
            EventSpeakerRequest.objects.filter(
                event_request=event_request,
                datetime=dt,
            ).values_list("event_speaker_id", flat=True)
        )
        event_speaker_requests += [
            EventSpeakerRequest(
                event_request=event_request,
                event_speaker_id=event_speaker_id,
                datetime=dt,
            )
            for event_speaker_id in possible_event_speaker_ids
            if event_speaker_id not in existing_speaker_ids
        ]

    if not commit:
        return event_speaker_requests

    return EventSpeakerRequest.objects.bulk_create(
        event_speaker_requests,
        ignore_conflicts=True,
        send_post_save_signal=True,
    )


def publish_event_assets(event_assets):
    event_assets = event_assets.filter(published=False)
    event_ids = set(event_assets.values_list("event_id", flat=True))
    result = event_assets.update(published=True)
    for event_id in event_ids:
        send_new_publish_event_asset_notification.delay(str(event_id))
    return result


def unpublish_event_assets(event_assets):
    return event_assets.filter(published=True).update(published=False)


def accept_event_request(event_request):
    event_speaker_requests = event_request.event_speaker_requests.filter(accepted=True)
    if event_speaker_requests.values("datetime").distinct().count() != 1:
        raise EventRequestValidationError(
            "Une seule date doit être sélectionnée pour valider la demande."
        )

    event_speakers = [esr.event_speaker for esr in event_speaker_requests]
    if not event_speakers:
        raise EventRequestValidationError(
            "Au moins un·e intervenant·e doit être sélectionné·e pour valider la demande."
        )
    start_time = event_speaker_requests.first().datetime

    with transaction.atomic():
        # Create the event
        event = create_event_for_event_request(
            event_request, event_speakers, start_time
        )

        # Change the event request event and status
        event_request.event = event
        event_request.status = EventRequest.Status.DONE
        event_request.save()

        # Schedule post-creation tasks
        transaction.on_commit(partial(schedule_new_event_tasks, event_request))


def accept_event_speaker_request(event_speaker_request):
    if event_speaker_request.accepted:
        raise EventSpeakerRequestValidationError(
            "L'intervenant·e choisi·e a déjà été validé·e pour la date indiquée."
        )

    event_request = event_speaker_request.event_request

    if not event_request.is_pending:
        raise EventSpeakerRequestValidationError(
            "Cette demande d'événement ne peut plus être validée."
        )

    if event_speaker_request.event_request.event is not None:
        raise EventSpeakerRequestValidationError(
            "Un événement a déjà été validé pour cette demande. Veuillez le supprimer avant d'en créer un autre."
        )

    if not event_speaker_request.available:
        raise EventSpeakerRequestValidationError(
            "L'intervenant·e choisi·e n'est pas disponible pour cette événement pour la date indiquée."
        )

    if (
        event_request.event_speaker_requests.filter(accepted=True)
        .exclude(datetime=event_speaker_request.datetime)
        .exists()
    ):
        raise EventSpeakerRequestValidationError(
            "Une date différente de celle choisie a déjà été validée pour cette demande."
        )

    with transaction.atomic():
        # Mark the event speaker request as accepted
        event_speaker_request.accepted = True
        event_speaker_request.save()

        if event_request.has_manual_validation:
            return

        # Mark all other event_speaker_requests as not accepted
        event_request.event_speaker_requests.exclude(
            pk=event_speaker_request.pk
        ).update(accepted=False)

        try:
            # accept the event_request
            accept_event_request(event_request)
        except EventRequestValidationError as e:
            raise EventSpeakerRequestValidationError(str(e))


def unaccept_event_speaker_request(event_speaker_request):
    if not event_speaker_request.accepted:
        raise EventSpeakerRequestValidationError(
            "L'intervenant·e choisi·e n'est validé·e pour la date indiquée."
        )

    if not event_speaker_request.is_unacceptable:
        raise EventSpeakerRequestValidationError(
            "Il n'est plus possible de valider l'intervenant·e choisi·e pour la date indiquée."
        )

    # Mark the event speaker request as unaccepted
    event_speaker_request.accepted = False
    event_speaker_request.save()
