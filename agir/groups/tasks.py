from collections import OrderedDict

from celery import shared_task
from django.conf import settings
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils.http import urlencode
from django.utils.translation import ugettext_lazy as _

from agir.authentication.tokens import subscription_confirmation_token_generator
from agir.events.models import Event, OrganizerConfig
from agir.lib.celery import emailing_task
from agir.lib.mailing import send_mosaico_email
from agir.lib.utils import front_url
from agir.people.actions.subscription import make_subscription_token
from agir.people.models import Person
from .actions.invitation import make_abusive_invitation_report_link
from .models import SupportGroup, Membership
from ..activity.models import Activity

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


@emailing_task
def send_support_group_creation_notification(membership_pk):
    try:
        membership = Membership.objects.select_related("supportgroup", "person").get(
            pk=membership_pk
        )
    except Membership.DoesNotExist:
        return

    group = membership.supportgroup
    referent = membership.person

    bindings = {
        "GROUP_NAME": group.name,
        "CONTACT_NAME": group.contact_name,
        "CONTACT_EMAIL": group.contact_email,
        "CONTACT_PHONE": group.contact_phone,
        "CONTACT_PHONE_VISIBILITY": _("caché")
        if group.contact_hide_phone
        else _("public"),
        "LOCATION_NAME": group.location_name,
        "LOCATION_ADDRESS": group.short_address,
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
def create_group_creation_confirmation_activity(membership_pk):
    try:
        membership = Membership.objects.select_related("supportgroup", "person").get(
            pk=membership_pk
        )
    except Membership.DoesNotExist:
        return

    referent = membership.person
    group = membership.supportgroup

    Activity.objects.create(
        type=Activity.TYPE_GROUP_CREATION_CONFIRMATION,
        recipient=referent,
        supportgroup=group,
        status=Activity.STATUS_UNDISPLAYED,
    )


@emailing_task
def send_support_group_changed_notification(support_group_pk, changed_data):
    try:
        group = SupportGroup.objects.get(pk=support_group_pk, published=True)
    except SupportGroup.DoesNotExist:
        return

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
def send_someone_joined_notification(membership_pk):
    try:
        membership = Membership.objects.select_related("person", "supportgroup").get(
            pk=membership_pk
        )
    except Membership.DoesNotExist:
        return

    person_information = str(membership.person)

    managers_filter = (Q(membership_type__gte=Membership.MEMBERSHIP_TYPE_MANAGER)) & Q(
        notifications_enabled=True
    )
    managing_membership = (
        membership.supportgroup.memberships.filter(managers_filter)
        .select_related("person")
        .prefetch_related("person__emails")
    )
    recipients = [membership.person for membership in managing_membership]

    Activity.objects.bulk_create(
        [
            Activity(
                type=Activity.TYPE_NEW_MEMBER,
                recipient=r,
                supportgroup=membership.supportgroup,
                individual=membership.person,
            )
            for r in recipients
        ]
    )

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
        recipients=recipients,
        bindings=bindings,
    )


@emailing_task
def send_external_join_confirmation(group_pk, email, **kwargs):
    try:
        group = SupportGroup.objects.get(pk=group_pk)
    except SupportGroup.DoesNotExist:
        return

    subscription_token = subscription_confirmation_token_generator.make_token(
        email=email, **kwargs
    )
    confirm_subscription_url = front_url(
        "external_join_group", args=[group_pk], auto_login=False
    )
    query_args = {"email": email, **kwargs, "token": subscription_token}
    confirm_subscription_url += "?" + urlencode(query_args)

    bindings = {"GROUP_NAME": group.name, "JOIN_LINK": confirm_subscription_url}

    send_mosaico_email(
        code="GROUP_EXTERNAL_JOIN_OPTIN",
        subject=_(f"Confirmez que vous souhaitez rejoindre « {group.name} »"),
        from_email=settings.EMAIL_FROM,
        recipients=[email],
        bindings=bindings,
    )


@emailing_task
def invite_to_group(group_id, invited_email, inviter_id):
    try:
        group = SupportGroup.objects.get(pk=group_id)
    except SupportGroup.DoesNotExist:
        return

    try:
        person = Person.objects.get_by_natural_key(invited_email)
    except Person.DoesNotExist:
        person = None

    group_name = group.name

    report_url = make_abusive_invitation_report_link(group_id, inviter_id)

    if person:
        Activity.objects.create(
            type=Activity.TYPE_GROUP_INVITATION, recipient=person, supportgroup=group,
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
def notify_new_group_event(group_pk, event_pk):
    try:
        group = SupportGroup.objects.get(pk=group_pk)
        event = Event.objects.get(pk=event_pk)
    except (SupportGroup.DoesNotExist, Event.DoesNotExist):
        return

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
        ]
    )
