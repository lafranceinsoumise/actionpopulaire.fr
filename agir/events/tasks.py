from collections import OrderedDict

import ics
import requests
from celery import shared_task
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils.http import urlencode
from django.utils.translation import ugettext_lazy as _
from requests import HTTPError
from urllib3 import Retry

from agir.authentication.subscription import subscription_confirmation_token_generator
from agir.lib.display import str_summary
from agir.lib.html import sanitize_html
from agir.people.models import Person
from ..lib.utils import front_url
from ..people.actions.mailing import send_mosaico_email
from .models import Event, RSVP, OrganizerConfig

a = requests.adapters.HTTPAdapter(max_retries=Retry(total=5, backoff_factor=1))
s = requests.Session()
s.mount("https://", a)

# encodes the preferred order when showing the messages
CHANGE_DESCRIPTION = OrderedDict(
    (
        ("information", _("les informations générales de l'événement")),
        ("location", _("le lieu de l'événement")),
        ("timing", _("les horaires de l'événements")),
        ("contact", _("les informations de contact des organisateurs")),
    )
)


@shared_task
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
        attachment=(
            "event.ics",
            str(ics.Calendar(events=[event.to_ics()])),
            "text/calendar",
        ),
    )


@shared_task
def send_event_changed_notification(event_pk, changes):
    try:
        event = Event.objects.get(pk=event_pk)
    except Event.DoesNotExist:
        # event does not exist anymore ?! nothing to do
        return

    change_descriptions = [
        desc for label, desc in CHANGE_DESCRIPTION.items() if label in changes
    ]
    change_fragment = render_to_string(
        template_name="lib/list_fragment.html", context={"items": change_descriptions}
    )

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
        "EVENT_CHANGES": change_fragment,
        "EVENT_LINK": front_url("view_event", kwargs={"pk": event_pk}),
        "EVENT_QUIT_LINK": front_url("quit_event", kwargs={"pk": event_pk}),
    }

    send_mosaico_email(
        code="EVENT_CHANGED",
        subject=_(
            "Les informations d'un événement auquel vous assistez ont été changées"
        ),
        from_email=settings.EMAIL_FROM,
        recipients=recipients,
        bindings=bindings,
        attachment=(
            "event.ics",
            str(ics.Calendar(events=[event.to_ics()])),
            "text/calendar",
        ),
    )


@shared_task
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
        attachment=(
            "event.ics",
            str(ics.Calendar(events=[rsvp.event.to_ics()])),
            "text/calendar",
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


@shared_task
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


@shared_task
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


@shared_task
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


@shared_task
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


@shared_task
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

    try:
        r = s.get(
            f"{settings.SCANNER_API}api/registrations/",
            auth=(settings.SCANNER_API_KEY, settings.SCANNER_API_SECRET),
            params={"event": rsvp.event.scanner_event, "uuid": str(rsvp.person.id)},
        )

        if len(r.json()) == 0:
            r = s.post(
                f"{settings.SCANNER_API}api/registrations/",
                auth=(settings.SCANNER_API_KEY, settings.SCANNER_API_SECRET),
                json=data,
            ).raise_for_status()
        else:
            r = s.patch(
                f"{settings.SCANNER_API}api/registrations/{r.json()[0]['id']}/",
                auth=(settings.SCANNER_API_KEY, settings.SCANNER_API_SECRET),
                json=data,
            ).raise_for_status()
    except HTTPError:
        print(r.text)
