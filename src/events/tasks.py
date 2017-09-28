from collections import OrderedDict
from urllib.parse import urljoin

from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.conf import settings
from django.shortcuts import reverse
from django.db.models import Q

from celery import shared_task

from lib.mails import send_mosaico_email

from .models import Event, RSVP, OrganizerConfig

# encodes the preferred order when showing the messages
CHANGE_DESCRIPTION = OrderedDict((
    ("information", _("les informations générales de l'événement")),
    ("location", _("le lieu de l'événement")),
    ("timing", _("les horaires de l'événements")),
    ("contact", _("les informations de contact des organisateurs"))
))


@shared_task
def send_event_creation_notification(organizer_config_pk):
    try:
        organizer_config = OrganizerConfig.objects.select_related('event', 'person').get(pk=organizer_config_pk)
    except OrganizerConfig.DoesNotExist:
        return

    event = organizer_config.event
    organizer = organizer_config.person

    bindings = {
        "EVENT_NAME": event.name,
        "CONTACT_NAME": event.contact_name,
        "CONTACT_EMAIL": event.contact_email,
        "CONTACT_PHONE": event.contact_phone,
        "CONTACT_PHONE_VISIBILITY": _("caché") if event.contact_hide_phone else _("public"),
        "LOCATION_NAME": event.location_name,
        "LOCATION_ADDRESS": event.short_address,
        "EVENT_LINK": urljoin(settings.APP_DOMAIN, "/groupes/details/{}".format(event.pk)),
        "MANAGE_EVENT_LINK": reverse('manage_event', kwargs={'pk': event.pk}, urlconf='front.urls'),
    }

    send_mosaico_email(
        code='EVENT_CREATION',
        subject=_("Les informations de votre nouveau groupe d'appui"),
        from_email=settings.EMAIL_FROM,
        recipients=[organizer.email],
        bindings=bindings,
    )


@shared_task
def send_event_changed_notification(event_pk, changes):
    try:
        event = Event.objects.get(pk=event_pk)
    except Event.DoesNotExist:
        # event does not exist anymore ?! nothing to do
        return

    change_descriptions = [desc for label, desc in CHANGE_DESCRIPTION.items() if label in changes]
    change_fragment = render_to_string(
        template_name='lib/list_fragment.html',
        context={'items': change_descriptions}
    )

    bindings = {
        "EVENT_NAME": event.name,
        "EVENT_CHANGES": change_fragment,
        "EVENT_LINK": urljoin(settings.APP_DOMAIN, "/evenements/details/{}".format(event_pk)),
        "EVENT_QUIT_LINK": urljoin(settings.FRONT_DOMAIN, reverse(
            "quit_event", kwargs={'pk': event_pk}, urlconf="front.urls"
        ))
    }

    notifications_enabled = Q(notifications_enabled=True) & Q(person__event_notifications=True)

    recipients = [rsvp.person.email for rsvp in event.rsvps.filter(notifications_enabled).select_related('person')]

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
        rsvp = RSVP.objects.select_related('person', 'event').get(pk=rsvp_pk)
    except RSVP.DoesNotExist:
        # RSVP does not exist any more?!
        return

    person_information = str(rsvp.person)

    recipients = [organizer_config.person.email
                  for organizer_config in rsvp.event.organizer_configs.filter(notifications_enabled=True)]

    bindings = {
        "EVENT_NAME": rsvp.event.name,
        "PERSON_INFORMATION": person_information,
        "MANAGE_EVENT_LINK": urljoin(
            settings.FRONT_DOMAIN,
            reverse("manage_event", kwargs={"pk": rsvp.event.pk}, urlconf="front.urls")
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

    notifications_enabled = Q(notifications_enabled=True) & Q(person__event_notifications=True)

    recipients = [rsvp.person.email for rsvp in event.rsvps.filter(notifications_enabled)]

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
