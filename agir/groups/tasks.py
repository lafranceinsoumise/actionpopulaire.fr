import smtplib
import socket
from collections import OrderedDict

from celery import shared_task
from django.conf import settings
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils.http import urlencode
from django.utils.translation import ugettext_lazy as _

from agir.authentication.signers import (
    subscription_confirmation_token_generator,
    invitation_confirmation_token_generator,
    abusive_invitation_report_token_generator,
)
from agir.lib.utils import front_url
from agir.lib.mailing import send_mosaico_email
from agir.people.models import Person
from .models import SupportGroup, Membership

# encodes the preferred order when showing the messages
CHANGE_DESCRIPTION = OrderedDict(
    (
        ("information", _("le nom ou la description du groupe")),
        ("location", _("le lieu de rencontre du groupe d'action")),
        ("contact", _("les informations de contact des animateurs du groupe")),
    )
)


@shared_task(max_retries=2, bind=True)
def send_support_group_creation_notification(self, membership_pk):
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

    try:
        send_mosaico_email(
            code="GROUP_CREATION",
            subject=_("Les informations de votre nouveau groupe d'action"),
            from_email=settings.EMAIL_FROM,
            recipients=[referent],
            bindings=bindings,
        )
    except (smtplib.SMTPException, socket.error) as exc:
        self.retry(countdown=60, exc=exc)


@shared_task(max_retries=2, bind=True)
def send_support_group_changed_notification(self, support_group_pk, changes):
    try:
        group = SupportGroup.objects.get(pk=support_group_pk, published=True)
    except SupportGroup.DoesNotExist:
        return

    change_descriptions = [
        desc for label, desc in CHANGE_DESCRIPTION.items() if label in changes
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
    try:
        send_mosaico_email(
            code="GROUP_CHANGED",
            subject=_("Les informations de votre groupe d'action ont été changées"),
            from_email=settings.EMAIL_FROM,
            recipients=recipients,
            bindings=bindings,
        )
    except (smtplib.SMTPException, socket.error) as exc:
        self.retry(countdown=60, exc=exc)


@shared_task(max_retries=2, bind=True)
def send_someone_joined_notification(self, membership_pk):
    try:
        membership = Membership.objects.select_related("person", "supportgroup").get(
            pk=membership_pk
        )
    except Membership.DoesNotExist:
        return

    person_information = str(membership.person)

    managers_filter = (Q(is_referent=True) | Q(is_manager=True)) & Q(
        notifications_enabled=True
    )
    managing_membership = (
        membership.supportgroup.memberships.filter(managers_filter)
        .select_related("person")
        .prefetch_related("person__emails")
    )
    recipients = [membership.person for membership in managing_membership]

    bindings = {
        "GROUP_NAME": membership.supportgroup.name,
        "PERSON_INFORMATION": person_information,
        "MANAGE_GROUP_LINK": front_url(
            "manage_group", kwargs={"pk": membership.supportgroup.pk}
        ),
    }

    try:
        send_mosaico_email(
            code="GROUP_SOMEONE_JOINED_NOTIFICATION",
            subject=_("Un nouveau membre dans votre groupe d'action"),
            from_email=settings.EMAIL_FROM,
            recipients=recipients,
            bindings=bindings,
        )
    except (smtplib.SMTPException, socket.error) as exc:
        self.retry(countdown=60, exc=exc)


@shared_task(max_retries=2, bind=True)
def send_external_join_confirmation(self, group_pk, email, **kwargs):
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

    try:
        send_mosaico_email(
            code="GROUP_EXTERNAL_JOIN_OPTIN",
            subject=_(f"Confirmez que vous souhaitez rejoindre « {group.name} »"),
            from_email=settings.EMAIL_FROM,
            recipients=[email],
            bindings=bindings,
        )
    except (smtplib.SMTPException, socket.error) as exc:
        self.retry(countdown=60, exc=exc)


@shared_task(max_retries=2, bind=True)
def invite_to_group(self, group_id, invited_email, inviter_id):
    try:
        group = SupportGroup.objects.get(pk=group_id)
    except SupportGroup.DoesNotExist:
        return

    try:
        person = Person.objects.get_by_natural_key(invited_email)
    except Person.DoesNotExist:
        person = None

    group_name = group.name

    report_params = {"group_id": group_id, "inviter_id": inviter_id}
    report_params["token"] = abusive_invitation_report_token_generator.make_token(
        **report_params
    )
    report_url = front_url("report_invitation_abuse", query=report_params)

    if person:
        invitation_token = invitation_confirmation_token_generator.make_token(
            person_id=person.pk, group_id=group_id
        )

        join_url = front_url(
            "invitation_confirmation",
            query={
                "person_id": person.id,
                "group_id": group_id,
                "token": invitation_token,
            },
        )

        try:
            send_mosaico_email(
                code="GROUP_INVITATION_MESSAGE",
                subject="Vous avez été invité à rejoindre un groupe de la FI",
                from_email=settings.EMAIL_FROM,
                recipients=[person],
                bindings={
                    "GROUP_NAME": group_name,
                    "CONFIRMATION_URL": join_url,
                    "REPORT_URL": report_url,
                },
            )
        except (smtplib.SMTPException, socket.error) as exc:
            self.retry(countdown=60, exc=exc)

    else:
        invitation_token = subscription_confirmation_token_generator.make_token(
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

        try:
            send_mosaico_email(
                code="GROUP_INVITATION_WITH_SUBSCRIPTION_MESSAGE",
                subject="Vous avez été invité à rejoindre la France insoumise",
                from_email=settings.EMAIL_FROM,
                recipients=[invited_email],
                bindings={
                    "GROUP_NAME": group_name,
                    "CONFIRMATION_URL": join_url,
                    "REPORT_URL": report_url,
                },
            )
        except (smtplib.SMTPException, socket.error) as exc:
            self.retry(countdown=60, exc=exc)


@shared_task(max_retries=2, bind=True)
def send_abuse_report_message(self, inviter_id):
    if not inviter_id:
        return

    try:
        inviter = Person.objects.get(pk=inviter_id)
    except Person.DoesNotExist:
        return

    try:
        send_mosaico_email(
            code="GROUP_INVITATION_ABUSE_MESSAGE",
            subject="Signalement pour invitation sans consentement",
            from_email=settings.EMAIL_FROM,
            recipients=[inviter],
        )
    except (smtplib.SMTPException, socket.error) as exc:
        self.retry(countdown=60, exc=exc)
