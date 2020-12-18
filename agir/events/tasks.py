from collections import OrderedDict

import ics
import requests
from celery import shared_task
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.http import urlencode
from django.utils.translation import ugettext_lazy as _

from agir.authentication.tokens import subscription_confirmation_token_generator
from agir.lib.celery import emailing_task, http_task
from agir.lib.display import str_summary
from agir.lib.html import sanitize_html
from agir.lib.geo import geocode_element
from agir.lib.mailing import send_mosaico_email
from agir.lib.utils import front_url
from agir.people.models import Person
from .models import Event, RSVP, OrganizerConfig

# encodes the preferred order when showing the messages
from agir.activity.models import Activity

NOTIFIED_CHANGES = {
    "name": "information",
    "start_time": "timing",
    "end_time": "timing",
    "contact_name": "contact",
    "contact_email": "contact",
    "contact_phone": "contact",
    "location_name": "location",
    "location_address1": "location",
    "location_address2": "location",
    "location_city": "location",
    "location_zip": "location",
    "location_country": "location",
    "description": "information",
    "facebook": "information",
}

CHANGE_DESCRIPTION = OrderedDict(
    (
        ("information", _("les informations générales de l'événement")),
        ("location", _("le lieu de l'événement")),
        ("timing", _("les horaires de l'événement")),
        ("contact", _("les informations de contact des organisateurs")),
    )
)


@emailing_task
def send_event_creation_notification(organizer_config_pk):
    try:
        organizer_config = OrganizerConfig.objects.select_related(
            "event", "person"
        ).get(pk=organizer_config_pk)
    except OrganizerConfig.DoesNotExist:
        return

    event = organizer_config.event
    organizer = organizer_config.person

    bindings = {
        "EVENT_NAME": event.name,
        "EVENT_SCHEDULE": event.get_display_date(),
        "CONTACT_NAME": event.contact_name,
        "CONTACT_EMAIL": event.contact_email,
        "CONTACT_PHONE": event.contact_phone,
        "CONTACT_PHONE_VISIBILITY": _("caché")
        if event.contact_hide_phone
        else _("public"),
        "LOCATION_NAME": event.location_name,
        "LOCATION_ADDRESS": event.short_address,
        "EVENT_LINK": front_url(
            "view_event", auto_login=False, kwargs={"pk": event.pk}
        ),
        "MANAGE_EVENT_LINK": front_url("manage_event", kwargs={"pk": event.pk}),
    }

    send_mosaico_email(
        code="EVENT_CREATION",
        subject=_("Les informations de votre nouvel événement"),
        from_email=settings.EMAIL_FROM,
        recipients=[organizer],
        bindings=bindings,
        attachments=(
            {
                "filename": "event.ics",
                "content": str(ics.Calendar(events=[event.to_ics()])),
                "mimetype": "text/calendar",
            },
        ),
    )


@emailing_task
def send_event_changed_notification(event_pk, changed_data):
    try:
        event = Event.objects.get(pk=event_pk)
    except Event.DoesNotExist:
        # event does not exist anymore ?! nothing to do
        return

    changed_data = [f for f in changed_data if f in NOTIFIED_CHANGES]

    if not changed_data:
        return

    changed_categories = {NOTIFIED_CHANGES[f] for f in changed_data}
    change_descriptions = [
        desc for id, desc in CHANGE_DESCRIPTION.items() if id in changed_categories
    ]
    change_fragment = render_to_string(
        template_name="lib/list_fragment.html", context={"items": change_descriptions}
    )

    notifications_enabled = Q(notifications_enabled=True) & Q(
        person__event_notifications=True
    )

    for r in event.attendees.all():
        activity = Activity.objects.filter(
            type=Activity.TYPE_EVENT_UPDATE,
            recipient=r,
            event=event,
            status=Activity.STATUS_UNDISPLAYED,
        ).first()
        if activity is not None:
            activity.meta["changed_data"] = list(
                set(changed_data).union(activity.meta["changed_data"])
            )
            activity.timestamp = timezone.now()
            activity.save()
        else:
            Activity.objects.create(
                type=Activity.TYPE_EVENT_UPDATE,
                recipient=r,
                event=event,
                meta={"changed_data": changed_data},
            )

    recipients = [
        rsvp.person
        for rsvp in event.rsvps.filter(notifications_enabled).prefetch_related(
            "person__emails"
        )
    ]

    bindings = {
        "EVENT_NAME": event.name,
        "EVENT_CHANGES": change_fragment,
        "EVENT_LINK": front_url("view_event", kwargs={"pk": event_pk}),
        "EVENT_QUIT_LINK": front_url("quit_event", kwargs={"pk": event_pk}),
    }
    send_mosaico_email(
        code="EVENT_CHANGED",
        subject=_(
            "Les informations d'un événement auquel vous participez ont été changées"
        ),
        from_email=settings.EMAIL_FROM,
        recipients=recipients,
        bindings=bindings,
        attachments=(
            {
                "filename": "event.ics",
                "content": str(ics.Calendar(events=[event.to_ics()])),
                "mimetype": "text/calendar",
            },
        ),
    )


@emailing_task
def send_rsvp_notification(rsvp_pk):
    try:
        rsvp = RSVP.objects.select_related("person", "event").get(pk=rsvp_pk)
    except RSVP.DoesNotExist:
        # RSVP does not exist any more?!
        return

    person_information = str(rsvp.person)

    recipients = [
        organizer_config.person
        for organizer_config in rsvp.event.organizer_configs.filter(
            notifications_enabled=True
        )
        if organizer_config.person != rsvp.person
    ]

    attendee_bindings = {
        "EVENT_NAME": rsvp.event.name,
        "EVENT_SCHEDULE": rsvp.event.get_display_date(),
        "CONTACT_NAME": rsvp.event.contact_name,
        "CONTACT_EMAIL": rsvp.event.contact_email,
        "LOCATION_NAME": rsvp.event.location_name,
        "LOCATION_ADDRESS": rsvp.event.short_address,
        "EVENT_LINK": front_url("view_event", auto_login=False, args=[rsvp.event.pk]),
    }

    send_mosaico_email(
        code="EVENT_RSVP_CONFIRMATION",
        subject=_("Confirmation de votre participation à l'événement"),
        from_email=settings.EMAIL_FROM,
        recipients=[rsvp.person],
        bindings=attendee_bindings,
        attachments=(
            {
                "filename": "event.ics",
                "content": str(ics.Calendar(events=[rsvp.event.to_ics()])),
                "mimetype": "text/calendar",
            },
        ),
    )

    if rsvp.event.rsvps.count() > 50:
        return

    organizer_bindings = {
        "EVENT_NAME": rsvp.event.name,
        "PERSON_INFORMATION": person_information,
        "MANAGE_EVENT_LINK": front_url("manage_event", kwargs={"pk": rsvp.event.pk}),
    }

    send_mosaico_email(
        code="EVENT_RSVP_NOTIFICATION",
        subject=_("Un nouveau participant à l'un de vos événements"),
        from_email=settings.EMAIL_FROM,
        recipients=recipients,
        bindings=organizer_bindings,
    )

    for r in recipients:
        # can merge activity with previous one if not displayed yet
        Activity.objects.create(
            recipient=r,
            type=Activity.TYPE_NEW_ATTENDEE,
            event=rsvp.event,
            individual=rsvp.person,
        )


@emailing_task
def send_guest_confirmation(rsvp_pk):
    try:
        rsvp = RSVP.objects.select_related("person", "event").get(pk=rsvp_pk)
    except RSVP.DoesNotExist:
        # RSVP does not exist any more?!
        return

    attendee_bindings = {
        "EVENT_NAME": rsvp.event.name,
        "EVENT_SCHEDULE": rsvp.event.get_display_date(),
        "CONTACT_NAME": rsvp.event.contact_name,
        "CONTACT_EMAIL": rsvp.event.contact_email,
        "LOCATION_NAME": rsvp.event.location_name,
        "LOCATION_ADDRESS": rsvp.event.short_address,
        "EVENT_LINK": front_url("view_event", args=[rsvp.event.pk]),
    }

    send_mosaico_email(
        code="EVENT_GUEST_CONFIRMATION",
        subject=_("Confirmation pour votre invité à l'événement"),
        from_email=settings.EMAIL_FROM,
        recipients=[rsvp.person],
        bindings=attendee_bindings,
    )


@emailing_task
def send_cancellation_notification(event_pk):
    try:
        event = Event.objects.get(pk=event_pk)
    except Event.DoesNotExist:
        return

    # check it is indeed cancelled
    if event.visibility != Event.VISIBILITY_ADMIN:
        return

    event_name = event.name

    notifications_enabled = Q(notifications_enabled=True) & Q(
        person__event_notifications=True
    )

    recipients = [
        rsvp.person
        for rsvp in event.rsvps.filter(notifications_enabled).prefetch_related(
            "person__emails"
        )
    ]

    bindings = {"EVENT_NAME": event_name}

    send_mosaico_email(
        code="EVENT_CANCELLATION",
        subject=_("Un événement auquel vous participiez a été annulé"),
        from_email=settings.EMAIL_FROM,
        recipients=recipients,
        bindings=bindings,
    )

    Activity.objects.bulk_create(
        Activity(type=Activity.TYPE_CANCELLED_EVENT, recipient=r, event=event,)
        for r in recipients
    )


@emailing_task
def send_external_rsvp_confirmation(event_pk, email, **kwargs):
    try:
        event = Event.objects.get(pk=event_pk)
    except ObjectDoesNotExist:
        return

    subscription_token = subscription_confirmation_token_generator.make_token(
        email=email, **kwargs
    )
    confirm_subscription_url = front_url(
        "external_rsvp_event", args=[event_pk], auto_login=False
    )
    query_args = {"email": email, **kwargs, "token": subscription_token}
    confirm_subscription_url += "?" + urlencode(query_args)

    bindings = {"EVENT_NAME": event.name, "RSVP_LINK": confirm_subscription_url}

    send_mosaico_email(
        code="EVENT_EXTERNAL_RSVP_OPTIN",
        subject=_("Merci de confirmer votre participation à l'événement"),
        from_email=settings.EMAIL_FROM,
        recipients=[email],
        bindings=bindings,
    )


@emailing_task
def send_event_report(event_pk):
    try:
        event = Event.objects.get(pk=event_pk)
    except Event.DoesNotExist:
        # event does not exist anymore ?! nothing to do
        return
    if event.report_summary_sent:
        return

    notifications_enabled = Q(notifications_enabled=True) & Q(
        person__event_notifications=True
    )
    recipients = [
        rsvp.person
        for rsvp in event.rsvps.filter(notifications_enabled).prefetch_related(
            "person__emails"
        )
    ]

    bindings = {
        "EVENT_NAME": event.name,
        "EVENT_REPORT_SUMMARY": sanitize_html(
            str_summary(event.report_content, length_max=500)
        ),
        "EVENT_REPORT_LINK": front_url("view_event", kwargs={"pk": event_pk}),
    }

    send_mosaico_email(
        code="EVENT_REPORT",
        subject=f"Compte-rendu de l'événement {event.name}",
        from_email=settings.EMAIL_FROM,
        recipients=recipients,
        bindings=bindings,
    )

    event.report_summary_sent = True
    event.save()


@http_task
def update_ticket(rsvp_pk, metas=None):
    try:
        rsvp = RSVP.objects.get(pk=rsvp_pk)
    except RSVP.DoesNotExist:
        return

    data = {
        "event": rsvp.event.scanner_event,
        "category": rsvp.event.scanner_category,
        "uuid": str(rsvp.person.id),
        "numero": str(rsvp.id),
        "full_name": rsvp.person.get_full_name(),
        "contact_email": rsvp.person.email,
        "gender": rsvp.person.gender,
        "metas": metas or {},
    }

    r = requests.get(
        f"{settings.SCANNER_API}api/registrations/",
        auth=(settings.SCANNER_API_KEY, settings.SCANNER_API_SECRET),
        params={"event": rsvp.event.scanner_event, "uuid": str(rsvp.person.id)},
    )

    if len(r.json()) == 0:
        r = requests.post(
            f"{settings.SCANNER_API}api/registrations/",
            auth=(settings.SCANNER_API_KEY, settings.SCANNER_API_SECRET),
            json=data,
        ).raise_for_status()
    else:
        r = requests.patch(
            f"{settings.SCANNER_API}api/registrations/{r.json()[0]['id']}/",
            auth=(settings.SCANNER_API_KEY, settings.SCANNER_API_SECRET),
            json=data,
        ).raise_for_status()


@emailing_task
def send_secretariat_notification(event_pk, person_pk, complete=True):
    try:
        event = Event.objects.get(pk=event_pk)
        person = Person.objects.get(pk=person_pk)
    except (Event.DoesNotExist, Person.DoesNotExist):
        return

    from agir.events.admin import EventAdmin

    bindings = {
        "EVENT_NAME": event.name,
        "EVENT_SCHEDULE": event.get_display_date(),
        "CONTACT_NAME": event.contact_name,
        "CONTACT_EMAIL": event.contact_email,
        "CONTACT_PHONE": event.contact_phone,
        "LOCATION_NAME": event.location_name,
        "LOCATION_ADDRESS": event.short_address,
        "EVENT_LINK": front_url("view_event", args=[event.pk]),
        "LEGAL_INFORMATIONS": EventAdmin.legal_informations(event),
    }

    send_mosaico_email(
        code="EVENT_SECRETARIAT_NOTIFICATION",
        subject=_(
            f"Événement {'complété' if complete else 'en attente'} : {str(event)}"
        ),
        from_email=settings.EMAIL_FROM,
        reply_to=[person.email],
        recipients=[settings.EMAIL_SECRETARIAT],
        bindings=bindings,
    )


@emailing_task
def send_organizer_validation_notification(event_pk):
    try:
        event = Event.objects.get(pk=event_pk)
    except (Event.DoesNotExist):
        return

    bindings = {
        "EVENT_NAME": event.name,
        "EVENT_SCHEDULE": event.get_display_date(),
        "LOCATION_NAME": event.location_name,
        "LOCATION_ADDRESS": event.short_address,
        "EVENT_LINK": front_url(
            "view_event", auto_login=False, kwargs={"pk": event.pk}
        ),
        "MANAGE_EVENT_LINK": front_url("manage_event", kwargs={"pk": event.pk}),
    }

    send_mosaico_email(
        code="EVENT_ORGANIZER_VALIDATION_NOTIFICATION",
        subject=_(f'Votre événement "{event.name}" a été publié'),
        from_email=settings.EMAIL_FROM,
        recipients=event.organizers.all(),
        bindings=bindings,
    )


@shared_task
def notify_on_event_report(event_pk):
    try:
        event = Event.objects.get(pk=event_pk)
    except (Event.DoesNotExist):
        return

    Activity.objects.bulk_create(
        Activity(type=Activity.TYPE_NEW_REPORT, recipient=r, event=event)
        for r in event.attendees.all()
    )


@http_task
def geocode_event(event_pk):
    try:
        event = Event.objects.get(pk=event_pk)
    except Event.DoesNotExist:
        return

    geocode_element(event)
    event.save()
