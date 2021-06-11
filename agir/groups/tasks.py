from collections import OrderedDict

from celery import shared_task
from django.conf import settings
from django.db.models import Q
from django.template.defaultfilters import date as _date
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import format_html_join, format_html
from django.utils.translation import ugettext_lazy as _

from agir.events.models import Event, OrganizerConfig
from agir.lib.celery import emailing_task, http_task, post_save_task
from agir.lib.geo import geocode_element
from agir.lib.mailing import send_mosaico_email
from agir.lib.utils import front_url
from agir.people.actions.subscription import make_subscription_token
from agir.people.models import Person
from .actions.invitation import make_abusive_invitation_report_link
from .models import SupportGroup, Membership
from ..activity.models import Activity
from ..lib.display import genrer
from ..msgs.models import SupportGroupMessage

NOTIFIED_CHANGES = {
    "name": "information",
    "contact_name": "contact",
    "contact_email": "contact",
    "contact_phone": "contact",
    "contact_hide_phone": "contact",
    "location_name": "location",
    "location_address1": "location",
    "location_address2": "location",
    "location_city": "location",
    "location_zip": "location",
    "location_country": "location",
    "description": "information",
}

CHANGE_DESCRIPTION = OrderedDict(
    (
        ("information", _("le nom ou la description du groupe")),
        ("location", _("le lieu de rencontre du groupe d'action")),
        ("contact", _("les informations de contact des animateurs du groupe")),
    )
)  # encodes the preferred order when showing the messages

GROUP_MEMBERSHIP_LIMIT_NOTIFICATION_STEPS = [
    0,  # 30 members
    -4,  # 26 members
    -9,  # 21 members
    -14,  # 16 members
    -19,  # 11 members
]


@emailing_task
@post_save_task
def send_support_group_creation_notification(membership_pk):
    membership = Membership.objects.select_related("supportgroup", "person").get(
        pk=membership_pk
    )
    group = membership.supportgroup
    referent = membership.person

    bindings = {
        "group_name": group.name,
        "GROUP_LINK": front_url(
            "view_group", auto_login=False, kwargs={"pk": group.pk}
        ),
        "MANAGE_GROUP_LINK": front_url("manage_group", kwargs={"pk": group.pk}),
    }

    send_mosaico_email(
        code="GROUP_CREATION",
        subject="Les informations de votre "
        + ("nouvelle équipe" if group.is_2022 else "nouveau groupe"),
        from_email=settings.EMAIL_FROM,
        recipients=[referent],
        bindings=bindings,
    )


@shared_task
@post_save_task
def create_group_creation_confirmation_activity(membership_pk):
    membership = Membership.objects.select_related("supportgroup", "person").get(
        pk=membership_pk
    )
    referent = membership.person
    group = membership.supportgroup

    Activity.objects.create(
        type=Activity.TYPE_GROUP_CREATION_CONFIRMATION,
        recipient=referent,
        supportgroup=group,
        status=Activity.STATUS_UNDISPLAYED,
    )


@emailing_task
@post_save_task
def send_support_group_changed_notification(support_group_pk, changed_data):
    group = SupportGroup.objects.get(pk=support_group_pk, published=True)
    changed_categories = {
        NOTIFIED_CHANGES[f] for f in changed_data if f in NOTIFIED_CHANGES
    }

    if not changed_categories:
        return

    for r in group.members.all():
        Activity.objects.create(
            type=Activity.TYPE_GROUP_INFO_UPDATE,
            recipient=r,
            supportgroup=group,
            meta={"changed_data": [f for f in changed_data if f in NOTIFIED_CHANGES]},
        )

    change_descriptions = [
        desc for id, desc in CHANGE_DESCRIPTION.items() if id in changed_categories
    ]
    change_fragment = render_to_string(
        template_name="lib/list_fragment.html", context={"items": change_descriptions}
    )

    bindings = {
        "GROUP_NAME": group.name,
        "GROUP_CHANGES": change_fragment,
        "GROUP_LINK": front_url("view_group", kwargs={"pk": support_group_pk}),
    }

    notifications_enabled = Q(notifications_enabled=True) & Q(
        person__group_notifications=True
    )

    recipients = [
        membership.person
        for membership in group.memberships.filter(
            notifications_enabled
        ).prefetch_related("person__emails")
    ]

    send_mosaico_email(
        code="GROUP_CHANGED",
        subject=_("Les informations de votre groupe d'action ont été changées"),
        from_email=settings.EMAIL_FROM,
        recipients=recipients,
        bindings=bindings,
    )


@emailing_task
@post_save_task
def send_joined_notification_email(membership_pk):
    membership = Membership.objects.select_related("person", "supportgroup").get(
        pk=membership_pk
    )
    person_information = str(membership.person)

    bindings = {
        "GROUP_NAME": membership.supportgroup.name,
        "PERSON_INFORMATION": person_information,
        "MANAGE_GROUP_LINK": front_url(
            "manage_group", kwargs={"pk": membership.supportgroup.pk}
        ),
    }
    send_mosaico_email(
        code="GROUP_SOMEONE_JOINED_NOTIFICATION",
        subject="Un nouveau membre dans votre "
        + ("équipe" if membership.supportgroup.is_2022 else "groupe"),
        from_email=settings.EMAIL_FROM,
        recipients=membership.supportgroup.managers,
        bindings=bindings,
    )


ALERT_CAPACITY_SUBJECTS = {
    21: "Votre équipe compte plus de 20 membres !",
    30: "Action requise : votre équipe ne respecte plus la charte des équipes de soutien",
}


@emailing_task
@post_save_task
def send_alert_capacity_email(supportgroup_pk, count):
    assert count in [21, 30]
    supportgroup = SupportGroup.objects.get(pk=supportgroup_pk)
    bindings = {
        "GROUP_NAME": supportgroup.name,
        "GROUP_NAME_URL": front_url("view_group", kwargs={"pk": supportgroup.pk}),
        "TRANSFER_LINK": front_url("transfer_group_members", args=(supportgroup.pk,)),
    }
    send_mosaico_email(
        code=f"GROUP_ALERT_CAPACITY_{str(count)}",
        subject=ALERT_CAPACITY_SUBJECTS[count],
        from_email=settings.EMAIL_FROM,
        recipients=supportgroup.referents,
        bindings=bindings,
    )


@emailing_task
@post_save_task
def invite_to_group(group_id, invited_email, inviter_id):
    group = SupportGroup.objects.get(pk=group_id)

    try:
        person = Person.objects.get_by_natural_key(invited_email)
    except Person.DoesNotExist:
        person = None

    group_name = group.name

    report_url = make_abusive_invitation_report_link(group_id, inviter_id)
    invitation_token = make_subscription_token(email=invited_email, group_id=group_id)
    join_url = front_url(
        "invitation_with_subscription_confirmation",
        query={
            "email": invited_email,
            "group_id": group_id,
            "token": invitation_token,
        },
    )

    if person:
        Activity.objects.create(
            type=Activity.TYPE_GROUP_INVITATION,
            recipient=person,
            supportgroup=group,
            meta={"joinUrl": join_url},
        )
    else:
        invitation_token = make_subscription_token(
            email=invited_email, group_id=group_id
        )
        join_url = front_url(
            "invitation_with_subscription_confirmation",
            query={
                "email": invited_email,
                "group_id": group_id,
                "token": invitation_token,
            },
        )

        send_mosaico_email(
            code="GROUP_INVITATION_WITH_SUBSCRIPTION_MESSAGE",
            subject="Vous avez été invité⋅e à rejoindre la France insoumise",
            from_email=settings.EMAIL_FROM,
            recipients=[invited_email],
            bindings={
                "GROUP_NAME": group_name,
                "CONFIRMATION_URL": join_url,
                "REPORT_URL": report_url,
            },
        )


@emailing_task
def send_abuse_report_message(inviter_id):
    if not inviter_id:
        return

    try:
        inviter = Person.objects.get(pk=inviter_id)
    except Person.DoesNotExist:
        return

    send_mosaico_email(
        code="GROUP_INVITATION_ABUSE_MESSAGE",
        subject="Signalement pour invitation sans consentement",
        from_email=settings.EMAIL_FROM,
        recipients=[inviter],
    )


@shared_task
@post_save_task
def notify_new_group_event(group_pk, event_pk):
    group = SupportGroup.objects.get(pk=group_pk)
    event = Event.objects.get(pk=event_pk)

    if not OrganizerConfig.objects.filter(event=event, as_group=group):
        return

    recipients = group.members.all()
    Activity.objects.bulk_create(
        [
            Activity(
                type=Activity.TYPE_NEW_EVENT_MYGROUPS,
                recipient=r,
                supportgroup=group,
                event=event,
            )
            for r in recipients
        ],
        send_post_save_signal=True,
    )


@post_save_task
@emailing_task
def send_new_group_event_email(group_pk, event_pk):
    group = SupportGroup.objects.get(pk=group_pk)
    event = Event.objects.get(pk=event_pk)

    if not OrganizerConfig.objects.filter(event=event, as_group=group):
        return

    recipients = group.members.filter(group_notifications=True)
    tz = timezone.get_current_timezone()
    now = timezone.now()
    start_time = event.start_time.astimezone(tz)
    simple_date = _date(start_time, "l j F").capitalize()
    bindings = {
        "GROUP": group.name.capitalize(),
        "EVENT_NAME": event.name.capitalize(),
        "EVENT_SCHEDULE": f"{simple_date} à {_date(start_time, 'G:i')}",
        "LOCATION_NAME": event.location_name,
        "LOCATION_ZIP": event.location_zip,
        "EVENT_LINK": event.get_absolute_url(),
    }
    formatted_start_date = simple_date
    if start_time - now < timezone.timedelta(days=7):
        formatted_start_date = f"Ce {_date(start_time, 'l')}"

    subject = f"{formatted_start_date} : {event.name.capitalize()} de {group.name.capitalize()}"
    send_mosaico_email(
        code="NEW_EVENT_MY_GROUPS_NOTIFICATION",
        subject=subject,
        from_email=settings.EMAIL_FROM,
        recipients=recipients,
        bindings=bindings,
    )


@emailing_task
def send_membership_transfer_sender_confirmation(bindings, recipients_pks):
    recipients = Person.objects.filter(pk__in=recipients_pks)

    send_mosaico_email(
        code="TRANSFER_SENDER",
        subject=f"{bindings['MEMBER_COUNT']} membres ont bien été transférés",
        from_email=settings.EMAIL_FROM,
        recipients=recipients,
        bindings=bindings,
    )


@emailing_task
def send_membership_transfer_receiver_confirmation(bindings, recipients_pks):
    recipients = Person.objects.filter(pk__in=recipients_pks)

    send_mosaico_email(
        code="TRANSFER_RECEIVER",
        subject=f"De nouveaux membres ont été transferés dans {bindings['GROUP_DESTINATION']}",
        from_email=settings.EMAIL_FROM,
        recipients=recipients,
        bindings=bindings,
    )


@emailing_task
@post_save_task
def send_membership_transfer_alert(bindings, recipient_pk):
    recipient = Person.objects.get(pk=recipient_pk)

    send_mosaico_email(
        code="TRANSFER_ALERT",
        subject=f"Notification de changement de groupe",
        from_email=settings.EMAIL_FROM,
        recipients=[recipient],
        bindings=bindings,
    )


@http_task
@post_save_task
def geocode_support_group(supportgroup_pk):
    supportgroup = SupportGroup.objects.get(pk=supportgroup_pk)

    geocode_element(supportgroup)
    supportgroup.save()

    if (
        supportgroup.coordinates_type is not None
        and supportgroup.coordinates_type >= SupportGroup.COORDINATES_NO_POSITION
    ):
        managers_filter = (
            Q(membership_type__gte=Membership.MEMBERSHIP_TYPE_MANAGER)
        ) & Q(notifications_enabled=True)
        managing_membership = supportgroup.memberships.filter(managers_filter)
        managing_membership_recipients = [
            membership.person for membership in managing_membership
        ]
        Activity.objects.bulk_create(
            [
                Activity(
                    type=Activity.TYPE_WAITING_LOCATION_GROUP,
                    recipient=r,
                    supportgroup=supportgroup,
                )
                for r in managing_membership_recipients
            ]
        )


@shared_task
@post_save_task
def create_accepted_invitation_member_activity(new_membership_pk):
    new_membership = Membership.objects.get(pk=new_membership_pk)

    managers_filter = (Q(membership_type__gte=Membership.MEMBERSHIP_TYPE_MANAGER)) & Q(
        notifications_enabled=True
    )
    managing_membership = new_membership.supportgroup.memberships.filter(
        managers_filter
    )
    recipients = [membership.person for membership in managing_membership]

    Activity.objects.bulk_create(
        [
            Activity(
                type=Activity.TYPE_ACCEPTED_INVITATION_MEMBER,
                recipient=r,
                supportgroup=new_membership.supportgroup,
                individual=new_membership.person,
            )
            for r in recipients
        ],
        send_post_save_signal=True,
    )


@emailing_task
@post_save_task
def send_message_notification_email(message_pk):
    message = SupportGroupMessage.objects.get(pk=message_pk)
    bindings = {
        "MESSAGE_HTML": format_html_join(
            "", "<p>{}</p>", ((p,) for p in message.text.split("\n"))
        ),
        "DISPLAY_NAME": message.author.display_name,
        "MESSAGE_LINK": front_url("user_message_details", kwargs={"pk": message_pk}),
        "AUTHOR_STATUS": format_html(
            '{} de <a href="{}">{}</a>',
            genrer(message.author.gender, "Animateur", "Animatrice", "Animateurice"),
            front_url("view_group", args=[message.supportgroup.pk]),
            message.supportgroup.name,
        ),
    }
    if message.subject:
        subject = message.subject
    else:
        subject = f"Vous avez un nouveau message de {message.author.display_name}"

    send_mosaico_email(
        code="NEW_MESSAGE",
        subject=subject,
        from_email=settings.EMAIL_FROM,
        recipients=message.supportgroup.members.filter(group_notifications=True),
        bindings=bindings,
    )
