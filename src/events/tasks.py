from collections import OrderedDict
from urllib.parse import urljoin

from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.conf import settings
from django.shortcuts import reverse

from celery import shared_task

from lib.mails import send_mosaico_email

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
        "EVENT_CHANGES": change_fragment,
        "EVENT_LINK": "#",
        "EVENT_QUIT_LINK": urljoin(settings.FRONT_DOMAIN, reverse("quit_event"))
    }

    recipients = [attendee.email for attendee in attendees]

    send_mosaico_email(
        code='',
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

    person_name = str(rsvp.person)

    # recipients = [organizer.email for organizer ]


@shared_task
def send_cancelation_notification(event_pk):
    pass
