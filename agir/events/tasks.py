import logging
from collections import OrderedDict
from datetime import timedelta

import ics
import requests
from celery import shared_task
from django.conf import settings
from django.template.defaultfilters import date as _date
from django.template.loader import render_to_string
from django.utils.formats import localize
from django.utils.html import format_html
from django.utils.http import urlencode
from django.utils.timezone import get_current_timezone
from django.utils.translation import gettext_lazy as _
from glom import T, Val

from agir.activity.models import Activity
from agir.authentication.tokens import subscription_confirmation_token_generator
from agir.groups.models import Membership
from agir.lib.celery import (
    emailing_task,
    post_save_task,
    http_task,
)
from agir.lib.display import str_summary
from agir.lib.geo import geocode_element
from agir.lib.google_sheet import (
    parse_sheet_link,
    copy_array_to_sheet,
    add_row_to_sheet,
)
from agir.lib.html import sanitize_html
from agir.lib.mailing import send_mosaico_email
from agir.lib.utils import front_url
from agir.notifications.models import Subscription
from agir.people.models import Person
from .display import display_participants, display_rsvp, display_identified_guest
from .models import (
    Event,
    RSVP,
    GroupAttendee,
    Invitation,
    OrganizerConfig,
    IdentifiedGuest,
)

logger = logging.getLogger(__name__)

# encodes the preferred order when showing the messages
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


@emailing_task(post_save=True)
def send_event_creation_notification(organizer_config_pk):
    organizer_config = OrganizerConfig.objects.select_related("event", "person").get(
        pk=organizer_config_pk
    )

    event = organizer_config.event
    organizer = organizer_config.person

    bindings = {
        "EVENT_NAME": event.name,
        "EVENT_SCHEDULE": event.get_display_date(),
        "LOCATION_NAME": event.location_name,
        "LOCATION_ADDRESS": event.short_address,
        "EVENT_LINK": front_url(
            "view_event", auto_login=False, kwargs={"pk": event.pk}
        ),
        "MANAGE_EVENT_LINK": front_url(
            "manage_event", auto_login=False, kwargs={"pk": event.pk}
        ),
        "DOCUMENTS_LINK": front_url(
            "event_project", auto_login=False, kwargs={"pk": event.pk}
        ),
        "EVENT_NAME_ENCODED": event.name,
        "EVENT_LINK_ENCODED": front_url(
            "view_event", auto_login=False, kwargs={"pk": event.pk}
        ),
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
                "content": ics.Calendar(
                    events=[event.to_ics(text_only_description=True)]
                ).serialize(),
                "mimetype": "text/calendar",
            },
        ),
    )


@emailing_task(post_save=True)
def send_event_changed_notification(event_pk, changed_data):
    event = Event.objects.get(pk=event_pk)

    changed_data = [f for f in changed_data if f in NOTIFIED_CHANGES]

    recipients = [
        r.person
        for r in event.rsvps.prefetch_related("person__emails").filter(
            person__notification_subscriptions__type=Subscription.SUBSCRIPTION_EMAIL,
            person__notification_subscriptions__activity_type=Activity.TYPE_EVENT_UPDATE,
        )
    ]

    if len(recipients) == 0:
        return

    changed_categories = {NOTIFIED_CHANGES[f] for f in changed_data}
    change_descriptions = [
        desc for id, desc in CHANGE_DESCRIPTION.items() if id in changed_categories
    ]
    change_fragment = render_to_string(
        template_name="lib/list_fragment.html", context={"items": change_descriptions}
    )

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
                "content": ics.Calendar(
                    events=[event.to_ics(text_only_description=True)]
                ).serialize(),
                "mimetype": "text/calendar",
            },
        ),
    )


@emailing_task(post_save=True)
def send_rsvp_notification(rsvp_pk):
    rsvp = RSVP.objects.select_related("person", "event").get(pk=rsvp_pk)
    person_information = str(rsvp.person)

    if rsvp.event.subscription_form:
        additional_message = format_html(
            '<div style="margin-top: 16px; padding: 16px; background-color: #EEE;">{}</div>',
            rsvp.event.subscription_form.html_confirmation_note(),
        )
    else:
        additional_message = ""

    attendee_bindings = {
        "EVENT_NAME": rsvp.event.name,
        "EVENT_SCHEDULE": rsvp.event.get_display_date(),
        "CONTACT_NAME": rsvp.event.contact_name,
        "CONTACT_EMAIL": rsvp.event.contact_email,
        "LOCATION_NAME": rsvp.event.location_name,
        "LOCATION_ADDRESS": rsvp.event.short_address,
        "EVENT_LINK": front_url("view_event", auto_login=False, args=[rsvp.event.pk]),
        "ADDITIONAL_INFORMATION": additional_message,
        "ATTENDANT_NOTICE": rsvp.event.attendant_notice,
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
                "content": ics.Calendar(
                    events=[rsvp.event.to_ics(text_only_description=True)]
                ).serialize(),
                "mimetype": "text/calendar",
            },
        ),
    )

    if rsvp.event.rsvps.count() > 50:
        return

    recipients = [
        organizer_config.person
        for organizer_config in rsvp.event.organizer_configs.all()
        if organizer_config.person != rsvp.person
    ]

    recipients_allowed_email = [
        s.person
        for s in Subscription.objects.prefetch_related("person__emails").filter(
            person__in=recipients,
            type=Subscription.SUBSCRIPTION_EMAIL,
            activity_type=Activity.TYPE_NEW_ATTENDEE,
        )
    ]

    organizer_bindings = {
        "EVENT_NAME": rsvp.event.name,
        "PERSON_INFORMATION": person_information,
        "MANAGE_EVENT_LINK": front_url("manage_event", kwargs={"pk": rsvp.event.pk}),
    }

    if len(recipients_allowed_email) > 0:
        send_mosaico_email(
            code="EVENT_RSVP_NOTIFICATION",
            subject=_("Un nouveau participant à l'un de vos événements"),
            from_email=settings.EMAIL_FROM,
            recipients=recipients_allowed_email,
            bindings=organizer_bindings,
        )

    # can merge activity with previous one if not displayed yet
    Activity.objects.bulk_create(
        [
            Activity(
                recipient=r,
                type=Activity.TYPE_NEW_ATTENDEE,
                event=rsvp.event,
                individual=rsvp.person,
            )
            for r in recipients
        ],
        send_post_save_signal=True,
    )


@post_save_task()
# Send notification new-group-attendee to all organizers (referents from groups co-organizing)
# Send notification new-event-participation-mygroups to members of group (not referents)
def send_group_attendee_notification(group_attendee_pk):
    group_attendee = GroupAttendee.objects.get(pk=group_attendee_pk)
    event = group_attendee.event
    supportgroup = group_attendee.group
    recipients = event.get_organizer_people()

    Activity.objects.bulk_create(
        [
            Activity(
                recipient=r,
                type=Activity.TYPE_NEW_GROUP_ATTENDEE,
                event=event,
                supportgroup=supportgroup,
            )
            for r in recipients
        ],
        send_post_save_signal=True,
    )

    # Send notification group_join_event to members
    members = Membership.objects.filter(
        supportgroup=supportgroup,
        membership_type__lt=Membership.MEMBERSHIP_TYPE_REFERENT,
    )
    recipients = [member.person for member in members]

    Activity.objects.bulk_create(
        [
            Activity(
                recipient=r,
                type=Activity.TYPE_NEW_EVENT_PARTICIPATION_MYGROUPS,
                event=event,
                supportgroup=supportgroup,
            )
            for r in recipients
        ],
        send_post_save_signal=True,
    )


@emailing_task(post_save=True)
def send_guest_confirmation(rsvp_pk):
    rsvp = RSVP.objects.select_related("person", "event").get(pk=rsvp_pk)

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


@emailing_task(post_save=True)
def send_cancellation_notification(event_pk):
    event = Event.objects.get(pk=event_pk)

    # check it is indeed cancelled
    if event.visibility != Event.VISIBILITY_ADMIN:
        return

    event_name = event.name

    recipients = [
        rsvp.person for rsvp in event.rsvps.prefetch_related("person__emails")
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
        [
            Activity(
                type=Activity.TYPE_CANCELLED_EVENT,
                recipient=r,
                event=event,
            )
            for r in recipients
        ],
        send_post_save_signal=True,
    )


@emailing_task(post_save=True)
def send_external_rsvp_confirmation(event_pk, email, **kwargs):
    event = Event.objects.get(pk=event_pk)
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


@emailing_task(post_save=True)
def send_event_report(event_pk):
    event = Event.objects.get(pk=event_pk)
    if event.report_summary_sent:
        return

    recipients = event.attendees.filter(
        notification_subscriptions__type=Subscription.SUBSCRIPTION_EMAIL,
        notification_subscriptions__activity_type=Activity.TYPE_NEW_REPORT,
        notification_subscriptions__membership__supportgroup__in=event.organizers_groups.all(),
    )

    if len(recipients) == 0:
        return

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


@http_task(post_save=True)
def update_ticket(rsvp_pk, metas=None):
    rsvp = RSVP.objects.get(pk=rsvp_pk)
    data = {
        "event": rsvp.event.scanner_event,
        "category": rsvp.event.scanner_category,
        "uuid": str(rsvp.person.id),
        "numero": str(rsvp.id),
        "full_name": rsvp.person.get_full_name(),
        "contact_email": rsvp.person.display_email,
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


@emailing_task(post_save=True)
def send_secretariat_notification(event_pk, person_pk, complete=True):
    event = Event.objects.get(pk=event_pk)
    person = Person.objects.get(pk=person_pk)

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


@emailing_task(post_save=True)
def send_organizer_validation_notification(event_pk):
    event = Event.objects.get(pk=event_pk)
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


@post_save_task()
def notify_on_event_report(event_pk):
    event = Event.objects.get(pk=event_pk)
    Activity.objects.bulk_create(
        [
            Activity(type=Activity.TYPE_NEW_REPORT, recipient=r, event=event)
            for r in event.attendees.all()
        ],
        send_post_save_signal=True,
    )


@http_task(post_save=True)
def geocode_event(event_pk):
    event = Event.objects.get(pk=event_pk)
    geocode_element(event)
    event.save()

    if (
        event.coordinates_type is not None
        and event.coordinates_type >= Event.COORDINATES_NO_POSITION
    ):
        Activity.objects.bulk_create(
            (
                Activity(
                    type=Activity.TYPE_WAITING_LOCATION_EVENT,
                    recipient=r,
                    event=event,
                )
                for r in event.organizers.all()
            ),
            send_post_save_signal=True,
        )


@emailing_task()
def send_pre_event_required_documents_reminder_email(event_pk):
    event = Event.objects.select_related("subtype").get(pk=event_pk)
    organizers = event.organizers.all()
    document_deadline = event.end_time + timedelta(days=15)

    bindings = {
        "EVENT_NAME": event.name,
        "DOCUMENTS_LINK": front_url(
            "event_project", auto_login=False, kwargs={"pk": event.pk}
        ),
        "DOCUMENT_DEADLINE": document_deadline.strftime("%d/%m"),
        "REQUIRED_DOCUMENT_TYPES": event.subtype.required_documents,
        "NEEDS_DOCUMENTS": len(event.subtype.required_documents) > 0,
    }

    send_mosaico_email(
        code="PRE_EVENT_REQUIRED_DOCUMENTS_REMINDER",
        subject=_("Votre événement a lieu demain : pensez aux justificatifs"),
        from_email=settings.EMAIL_FROM,
        recipients=[organizer for organizer in organizers],
        bindings=bindings,
    )


@emailing_task()
def send_post_event_required_documents_reminder_email(event_pk):
    event = Event.objects.select_related("subtype").get(pk=event_pk)
    organizers = event.organizers.all()
    document_deadline = event.end_time + timedelta(days=15)

    bindings = {
        "EVENT_NAME": event.name,
        "DOCUMENTS_LINK": front_url(
            "event_project", auto_login=False, kwargs={"pk": event.pk}
        ),
        "DOCUMENT_DEADLINE": document_deadline.strftime("%d/%m"),
        "REQUIRED_DOCUMENT_TYPES": event.subtype.required_documents,
        "NEEDS_DOCUMENTS": len(event.subtype.required_documents) > 0,
    }

    send_mosaico_email(
        code="POST_EVENT_REQUIRED_DOCUMENTS_REMINDER",
        subject=_("Rappel : envoyez les justificatifs de l'événement d'hier"),
        from_email=settings.EMAIL_FROM,
        recipients=[organizer for organizer in organizers],
        bindings=bindings,
    )


@emailing_task()
def send_event_suggestion_email(event_pk, recipient_pk):
    try:
        event = Event.objects.get(pk=event_pk)
    except Event.DoesNotExist:
        return

    subscription = Subscription.objects.filter(
        person_id=recipient_pk,
        type=Subscription.SUBSCRIPTION_EMAIL,
        activity_type=Activity.TYPE_EVENT_SUGGESTION,
    )

    if not subscription.exists():
        return

    group = event.organizers_groups.first()
    if group is not None:
        subject = f"Participez à l'action de {group.name.capitalize()} !"
    else:
        subject = "Participez à cette action !"

    start_time = event.local_start_time
    simple_date = _date(start_time, "l j F").capitalize()
    event_image = event.get_absolute_image_url()

    bindings = {
        "TITLE": subject,
        "EVENT_NAME": event.name.capitalize(),
        "EVENT_SCHEDULE": f"{simple_date} à {_date(start_time, 'G:i')}",
        "LOCATION_NAME": event.location_name,
        "LOCATION_ZIP": event.location_zip,
        "EVENT_LINK": event.get_absolute_url(),
        "EVENT_DESCRIPTION": sanitize_html(event.description)
        if event.description
        else None,
        "EVENT_IMAGE": event_image,
    }

    send_mosaico_email(
        code="EVENT_SUGGESTION",
        subject=subject,
        from_email=settings.EMAIL_FROM,
        recipients=[subscription.first().person],
        bindings=bindings,
        attachments=(
            {
                "filename": "event.ics",
                "content": ics.Calendar(
                    events=[event.to_ics(text_only_description=True)]
                ).serialize(),
                "mimetype": "text/calendar",
            },
        ),
    )


@emailing_task(post_save=True)
def send_group_coorganization_invitation_notification(invitation_pk):
    invitation = Invitation.objects.get(pk=invitation_pk)
    event = invitation.event
    group = invitation.group
    member = invitation.person_sender

    subject = f"Votre groupe {group.name} est invité à co-organiser {event.name}"
    recipients = group.referents

    bindings = {
        "TITLE": subject,
        "EVENT_NAME": event.name,
        "GROUP_NAME": group.name,
        "MEMBER": member.display_name,
        "DATE": f"{_date(event.local_start_time, 'l j F').capitalize()} à {_date(event.local_start_time, 'G:i')}",
        "EVENT_LINK": event.get_absolute_url(),
        "ACCEPT_LINK": front_url(
            "accept_event_group_coorganization",
            kwargs={"pk": invitation_pk},
        ),
        "REFUSE_LINK": front_url(
            "refuse_event_group_coorganization",
            kwargs={"pk": invitation_pk},
        ),
    }

    send_mosaico_email(
        code="EVENT_GROUP_COORGANIZATION_INVITE",
        subject=subject,
        from_email=settings.EMAIL_FROM,
        recipients=recipients,
        bindings=bindings,
        attachments=(
            {
                "filename": "event.ics",
                "content": ics.Calendar(
                    events=[event.to_ics(text_only_description=True)]
                ).serialize(),
                "mimetype": "text/calendar",
            },
        ),
    )

    # Add activity for all group referents that hasnt been notified yet
    Activity.objects.bulk_create(
        [
            Activity(
                type=Activity.TYPE_GROUP_COORGANIZATION_INVITE,
                recipient=r,
                event=event,
                supportgroup=group,
                individual=invitation.person_sender,
                meta={
                    "acceptUrl": front_url(
                        "accept_event_group_coorganization",
                        absolute=False,
                        kwargs={"pk": invitation_pk},
                    ),
                    "refuseUrl": front_url(
                        "refuse_event_group_coorganization",
                        absolute=False,
                        kwargs={"pk": invitation_pk},
                    ),
                },
            )
            for r in recipients
        ],
        send_post_save_signal=True,
    )


@emailing_task(post_save=True)
def send_accepted_group_coorganization_invitation_notification(invitation_id):
    invitation = Invitation.objects.get(pk=invitation_id)
    event = invitation.event
    group = invitation.group
    group_member_ids = group.members.values_list("id", flat=True)
    recipients = [
        person
        for person in event.get_organizer_people()
        if person.id not in group_member_ids
    ]

    # Add activity to current organizers
    Activity.objects.bulk_create(
        [
            Activity(
                type=Activity.TYPE_GROUP_COORGANIZATION_ACCEPTED_FROM,
                recipient=r,
                event=event,
                supportgroup=group,
            )
            for r in recipients
        ],
        send_post_save_signal=True,
    )

    # Add activity to new organizers of group invited (group referents)
    Activity.objects.bulk_create(
        [
            Activity(
                type=Activity.TYPE_GROUP_COORGANIZATION_ACCEPTED_TO,
                recipient=r,
                event=event,
                supportgroup=group,
            )
            for r in group.referents
        ],
        send_post_save_signal=True,
    )

    subject = f"{group.name} a accepté de co-organiser {event.name}"

    bindings = {
        "TITLE": subject,
        "EVENT_NAME": event.name,
        "EVENT_LINK": event.get_absolute_url(),
        "GROUP_NAME": group.name,
        "DATE": f"{_date(event.local_start_time, 'l j F').capitalize()} à {_date(event.local_start_time, 'G:i')}",
    }

    send_mosaico_email(
        code="EVENT_GROUP_COORGANIZATION_ACCEPTED",
        subject=subject,
        from_email=settings.EMAIL_FROM,
        recipients=recipients,
        bindings=bindings,
    )


@emailing_task(post_save=True)
def send_refused_group_coorganization_invitation_notification(invitation_id):
    invitation = Invitation.objects.get(pk=invitation_id)
    event = invitation.event
    group = invitation.group
    group_member_ids = group.members.values_list("id", flat=True)
    recipients = [
        person
        for person in event.get_organizer_people()
        if person.id not in group_member_ids
    ]

    subject = f"{group.name} a refusé de co-organiser {event.name}"

    bindings = {
        "TITLE": subject,
        "EVENT_NAME": event.name,
        "GROUP_NAME": group.name,
        "DATE": f"{_date(event.local_start_time, 'l j F').capitalize()} à {_date(event.local_start_time, 'G:i')}",
    }

    send_mosaico_email(
        code="EVENT_GROUP_COORGANIZATION_REFUSED",
        subject=subject,
        from_email=settings.EMAIL_FROM,
        recipients=recipients,
        bindings=bindings,
    )


@emailing_task()
def send_event_report_form_reminder_email(event_pk):
    event = Event.objects.select_related("subtype", "subtype__report_person_form").get(
        pk=event_pk
    )
    bindings = {
        "EVENT_SUBTYPE": event.subtype.description,
        "EVENT_DATE": event.local_end_time.strftime("%d %B %Y"),
        "FORM_NAME": event.subtype.report_person_form.title,
        "FORM_DESCRIPTION": event.subtype.report_person_form.short_description,
        "FORM_LINK": front_url(
            "view_person_form",
            kwargs={"slug": event.subtype.report_person_form.slug},
            query={"reported_event_id": str(event_pk)},
        ),
    }

    send_mosaico_email(
        code="EVENT_REPORT_FORM_REMINDER",
        subject=_(f"Bilan de votre événement {event.name}"),
        from_email=settings.EMAIL_FROM,
        recipients=event.organizers.all(),
        bindings=bindings,
    )


SPEC_RSVP = {
    "id": ("id", "R{}".format),
    "created": (T.created.astimezone(get_current_timezone()), localize),
    "person_id": ("person_id", str),
    "email": "person.email",
    "status": T.get_status_display(),
}

SPEC_IDENTIFIED_GUEST = {
    **SPEC_RSVP,
    "id": ("id", "I{}".format),
    "created": Val(""),
    "person_id": ("rsvp.person_id", str),
    "email": "rsvp.person.email",
}

SPEC_PAYMENT = {
    "montant": ("price", T / 100),
    "status": T.get_status_display(),
    "mode de paiement": "mode",
}


@shared_task
def copier_participants_vers_feuille_externe(event_id):
    try:
        event = Event.objects.select_related("subscription_form").get(id=event_id)
    except Event.DoesNotExist:
        return

    sheet_id = parse_sheet_link(event.lien_feuille_externe)

    if not sheet_id:
        logger.warning(
            f"URL de la Google sheet incorrecte pour l'événement d'id {event.id}"
        )
        return

    values = display_participants(event)

    copy_array_to_sheet(sheet_id, values)


@shared_task
def copier_rsvp_vers_feuille_externe(rsvp_id):
    try:
        rsvp = RSVP.objects.select_related(
            "form_submission", "person", "payment", "event"
        ).get(id=rsvp_id)
    except RSVP.DoesNotExist:
        return

    sheet_id = parse_sheet_link(rsvp.event.lien_feuille_externe)

    if not sheet_id:
        logger.warning(
            f"URL de la Google sheet incorrecte pour l'événement d'id {rsvp.event.id}"
        )
        return

    values = display_rsvp(rsvp)

    add_row_to_sheet(sheet_id, values, "id")


@shared_task
def copier_identified_guest_vers_feuille_externe(guest_id):
    try:
        ig = IdentifiedGuest.objects.select_related(
            "submission", "rsvp__event", "rsvp__person", "payment"
        ).get(id=guest_id)
    except IdentifiedGuest.DoesNotExist:
        return

    sheet_id = parse_sheet_link(ig.rsvp.event.lien_feuille_externe)

    if not sheet_id:
        logger.warning(
            f"URL de la Google sheet incorrecte pour l'événement d'id {ig.rsvp.event.id}"
        )
        return

    values = display_identified_guest(ig)

    add_row_to_sheet(sheet_id, values, "id")
