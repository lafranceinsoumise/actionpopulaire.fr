from collections import OrderedDict
from urllib.parse import urljoin

from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.conf import settings
from django.shortcuts import reverse

from celery import shared_task

from lib.mails import send_mosaico_email
from front import urls as front_urls

from .models import Event, RSVP

# encodes the preferred order when showing the messages
CHANGE_DESCRIPTION = OrderedDict((
    ("information", _("les informations générales de l'événement")),
    ("location", _("le lieu de l'événement")),
    ("timing", _("les horaires de l'événements")),
    ("contact", _("les informations de contact des organisateurs"))
))


@shared_task
def send_event_changed_notification(event_pk, changes):
    try:
        event = Event.objects.get(pk=event_pk)
    except Event.DoesNotExist:
        # event does not exist anymore ?! nothing to do
        return

    attendees = event.attendees.all()

    change_descriptions = [desc for label, desc in CHANGE_DESCRIPTION.items() if label in changes]
    change_fragment = render_to_string(
        template_name='lib/list_fragment.html',
        context={'items': change_descriptions}
    )

    # TODO: find adequate way to set up domain names to use for these links
    bindings = {
        "EVENT_NAME": event.changes,
        "EVENT_CHANGES": change_fragment,
        "EVENT_LINK": "#",
        "EVENT_QUIT_LINK": urljoin(settings.FRONT_DOMAIN, reverse("quit_event", urlconf=front_urls))
    }

    recipients = [attendee.email for attendee in attendees]

    send_mosaico_email(
        code='EVENT_CHANGED',
        subject=_("Les informations d'un événement auquel vous assistez ont été changées"),
        from_email=settings.EMAIL_FROM,
        recipients=recipients,
        bindings=bindings,
    )


@shared_task
def send_rsvp_notification(rsvp_pk):
    try:
        rsvp = RSVP.objects.get(pk=rsvp_pk)
    except RSVP.DoesNotExist:
        # RSVP does not exist any more?!
        return

    person_information = str(rsvp.person)

    recipients = [organizer_config.person.email
                  for organizer_config in rsvp.event.organizer_configs
                  if organizer_config.send_notifications]

    bindings = {
        "EVENT_NAME": rsvp.event.name,
        "PERSON_INFORMATION": person_information,
        "MANAGE_EVENT_LINK": urljoin(
            settings.FRONT_DOMAIN,
            reverse("manage_event", kwargs={"pk": rsvp.event.pk}, urlconf=front_urls)
        )
    }

    send_mosaico_email(
        code='EVENT_RSVP_NOTIFICATION',
        subject=_("Un nouveau participant à l'un de vos événements"),
        from_email=settings.EMAIL_FROM,
        recipients=recipients,
        bindings=bindings
    )


@shared_task
def send_cancellation_notification(event_pk):
    try:
        event = Event.objects.get(pk=event_pk)
    except Event.DoesNotExist:
        return

    # check it is indeed cancelled
    if event.published:
        return

    event_name = event.name

    recipients = [rsvp.person.email for rsvp in event.rsvps.all()]

    bindings = {
        "EVENT_NAME": event_name
    }

    send_mosaico_email(
        code='EVENT_CANCELLATION',
        subject=_("Un événement auquel vous participiez a été annulé"),
        from_email=settings.EMAIL_FROM,
        recipients=recipients,
        bindings=bindings
    )
