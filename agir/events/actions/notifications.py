from django.db import transaction, IntegrityError

from agir.activity.models import Activity
from agir.events.models import Event


def new_event_suggestion_notification(event, recipient):
    activity_config = {
        "type": Activity.TYPE_EVENT_SUGGESTION,
        "event": event,
    }
    if event.organizers_groups.count() > 0:
        activity_config["supportgroup"] = event.organizers_groups.first()
    else:
        activity_config["individual"] = event.organizers.first()

    try:
        Activity.objects.create(
            **activity_config,
            recipient=recipient,
        )
    except IntegrityError:
        pass


@transaction.atomic()
def event_required_document_reminder_notification(event_pk, post=False, pre=False):
    activity_type = None
    if post:
        activity_type = Activity.TYPE_REMINDER_DOCS_EVENT_NEXTDAY
    elif pre:
        activity_type = Activity.TYPE_REMINDER_DOCS_EVENT_EVE
    if activity_type is None:
        return

    try:
        event = Event.objects.get(pk=event_pk)
    except Event.DoesNotExist:
        return

    Activity.objects.bulk_create(
        [
            Activity(
                type=activity_type,
                recipient=organizer,
                event=event,
            )
            for organizer in event.organizers.all()
        ],
        send_post_save_signal=True,
    )


@transaction.atomic()
def event_report_form_reminder_notification(event_pk):
    try:
        event = Event.objects.get(pk=event_pk)
        form = event.subtype.report_person_form
    except Event.DoesNotExist:
        return

    if (
        form is None
        or not form.published
        or form.submissions.filter(data__reported_event_id=event_pk).exists()
    ):
        return

    meta = {
        "title": form.title,
        "description": form.meta_description,
        "slug": form.slug,
    }

    Activity.objects.bulk_create(
        [
            Activity(
                type=Activity.TYPE_REMINDER_REPORT_FORM_FOR_EVENT,
                recipient=organizer,
                event=event,
                meta=meta,
            )
            for organizer in event.organizers.all()
        ],
        send_post_save_signal=True,
    )


@transaction.atomic()
def upcoming_event_start_reminder_notification(event_pk):
    try:
        event = Event.objects.get(pk=event_pk)
    except Event.DoesNotExist:
        return

    Activity.objects.bulk_create(
        [
            Activity(
                type=Activity.TYPE_REMINDER_UPCOMING_EVENT_START,
                recipient=attendee,
                event=event,
            )
            for attendee in event.confirmed_attendees
        ],
        send_post_save_signal=True,
    )
