from collections import OrderedDict

import ics
import reversion
from django.conf import settings
from django.db.models import Q
from django.template.defaultfilters import date as _date
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import format_html_join, format_html
from django.utils.translation import gettext_lazy as _

from agir.activity.models import Activity
from agir.events.models import Event, OrganizerConfig
from agir.groups.display import genrer_membership
from agir.groups.models import SupportGroup, Membership
from agir.lib.celery import (
    emailing_task,
    post_save_task,
    http_task,
)
from agir.lib.geo import geocode_element
from agir.lib.html import sanitize_html
from agir.lib.mailing import send_mosaico_email, send_template_email
from agir.lib.utils import clean_subject_email
from agir.lib.utils import front_url
from agir.msgs.models import SupportGroupMessage, SupportGroupMessageComment
from agir.notifications.models import Subscription
from agir.people.actions.subscription import make_subscription_token
from agir.people.models import Person
from .actions.invitation import make_abusive_invitation_report_link
from .utils.certification import check_certification_criteria
from ..msgs.actions import (
    get_comment_recipients,
    get_comment_participants,
    filter_with_subscription,
)

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
    # 0,  # 30 members (disabled until further notice)
    -4,  # 26 members
    -9,  # 21 members
    -14,  # 16 members
    -19,  # 11 members
]


@emailing_task(post_save=True)
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
        subject="Les informations de votre nouveau groupe",
        from_email=settings.EMAIL_FROM,
        recipients=[referent],
        bindings=bindings,
    )


@post_save_task()
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


@emailing_task(post_save=True)
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

    recipients = Person.objects.filter(
        notification_subscriptions__membership__supportgroup=group,
        notification_subscriptions__type=Subscription.SUBSCRIPTION_EMAIL,
        notification_subscriptions__activity_type=Activity.TYPE_GROUP_INFO_UPDATE,
    )

    if len(recipients) == 0:
        return

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

    send_mosaico_email(
        code="GROUP_CHANGED",
        subject=_("Les informations de votre groupe d'action ont été changées"),
        from_email=settings.EMAIL_FROM,
        recipients=recipients,
        bindings=bindings,
    )


@emailing_task(post_save=True)
def send_joined_notification_email(membership_pk):
    membership = Membership.objects.select_related("person", "supportgroup").get(
        pk=membership_pk
    )
    person_information = str(membership.person)

    recipients = Person.objects.filter(
        notification_subscriptions__membership__supportgroup=membership.supportgroup,
        notification_subscriptions__membership__membership_type__gte=Membership.MEMBERSHIP_TYPE_MANAGER,
        notification_subscriptions__type=Subscription.SUBSCRIPTION_EMAIL,
        notification_subscriptions__activity_type=Activity.TYPE_NEW_MEMBER,
    )

    if len(recipients) == 0:
        return

    bindings = {
        "GROUP_NAME": membership.supportgroup.name,
        "PERSON_INFORMATION": person_information,
        "MANAGE_GROUP_LINK": front_url(
            "manage_group", kwargs={"pk": membership.supportgroup.pk}
        ),
    }
    send_mosaico_email(
        code="GROUP_SOMEONE_JOINED_NOTIFICATION",
        subject="Un nouveau membre dans votre groupe",
        from_email=settings.EMAIL_FROM,
        recipients=recipients,
        bindings=bindings,
    )


ALERT_CAPACITY_SUBJECTS = {
    21: "Votre groupe compte plus de 20 membres !",
    30: "Action requise : votre groupe ne respecte plus la charte des groupes d'action",
}


@emailing_task(post_save=True)
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


@emailing_task(post_save=True)
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


@emailing_task()
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


@post_save_task()
def notify_new_group_event(group_pk, event_pk):
    if not OrganizerConfig.objects.filter(event_id=event_pk, as_group_id=group_pk):
        return

    recipients = Person.objects.filter(
        notification_subscriptions__membership__supportgroup_id=group_pk,
        notification_subscriptions__type=Subscription.SUBSCRIPTION_PUSH,
        notification_subscriptions__activity_type=Activity.TYPE_NEW_EVENT_MYGROUPS,
    )
    # Exclude other organizing group members from notification to avoid duplicates
    other_organizing_group_members = (
        Membership.objects.exclude(supportgroup_id=group_pk)
        .filter(
            supportgroup_id__in=(
                OrganizerConfig.objects.filter(
                    event_id=event_pk, as_group_id__isnull=False
                ).values_list("as_group_id", flat=True)
            )
        )
        .values_list("person_id", flat=True)
    )

    if len(other_organizing_group_members) > 0:
        recipients = recipients.exclude(id__in=other_organizing_group_members)

    if len(recipients) == 0:
        return

    group = SupportGroup.objects.get(pk=group_pk)
    event = Event.objects.get(pk=event_pk)
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


@emailing_task(post_save=True)
def send_new_group_event_email(group_pk, event_pk):
    if not OrganizerConfig.objects.filter(event_id=event_pk, as_group_id=group_pk):
        return

    recipients = Person.objects.filter(
        notification_subscriptions__membership__supportgroup_id=group_pk,
        notification_subscriptions__type=Subscription.SUBSCRIPTION_EMAIL,
        notification_subscriptions__activity_type=Activity.TYPE_NEW_EVENT_MYGROUPS,
    )
    # Exclude other organizing group members from notification to avoid duplicates
    other_organizing_group_members = (
        Membership.objects.exclude(supportgroup_id=group_pk)
        .filter(
            supportgroup_id__in=(
                OrganizerConfig.objects.filter(
                    event_id=event_pk, as_group_id__isnull=False
                ).values_list("as_group_id", flat=True)
            )
        )
        .values_list("person_id", flat=True)
    )

    if len(other_organizing_group_members) > 0:
        recipients = recipients.exclude(id__in=other_organizing_group_members)

    if len(recipients) == 0:
        return

    group = SupportGroup.objects.get(pk=group_pk)
    event = Event.objects.get(pk=event_pk)

    now = timezone.now()
    start_time = event.local_start_time
    simple_date = _date(start_time, "l j F").capitalize()
    event_image = event.get_absolute_image_url()

    bindings = {
        "GROUP": group.name.capitalize(),
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


@emailing_task()
def send_membership_transfer_sender_confirmation(bindings, recipients_pks):
    recipients = Person.objects.filter(pk__in=recipients_pks)

    send_mosaico_email(
        code="TRANSFER_SENDER",
        subject=f"{bindings['MEMBER_COUNT']} membres ont bien été transférés",
        from_email=settings.EMAIL_FROM,
        recipients=recipients,
        bindings=bindings,
    )


@emailing_task()
def send_membership_transfer_receiver_confirmation(bindings, recipients_pks):
    recipients = Person.objects.filter(
        pk__in=recipients_pks,
        notification_subscriptions__type=Subscription.SUBSCRIPTION_EMAIL,
        notification_subscriptions__activity_type=Activity.TYPE_NEW_MEMBERS_THROUGH_TRANSFER,
    )

    if len(recipients) == 0:
        return

    send_mosaico_email(
        code="TRANSFER_RECEIVER",
        subject=f"De nouveaux membres ont été transférés dans {bindings['GROUP_DESTINATION']}",
        from_email=settings.EMAIL_FROM,
        recipients=recipients,
        bindings=bindings,
    )


@emailing_task(post_save=True)
def send_membership_transfer_alert(bindings, recipient_pk):
    recipient = Person.objects.get(pk=recipient_pk)

    send_mosaico_email(
        code="TRANSFER_ALERT",
        subject=f"Notification de changement de groupe",
        from_email=settings.EMAIL_FROM,
        recipients=[recipient],
        bindings=bindings,
    )


@http_task(post_save=True)
def geocode_support_group(supportgroup_pk):
    supportgroup = SupportGroup.objects.get(pk=supportgroup_pk)

    geocode_element(supportgroup)
    supportgroup.save()

    if (
        supportgroup.coordinates_type is not None
        and supportgroup.coordinates_type >= SupportGroup.COORDINATES_NO_POSITION
    ):
        managers_filter = Q(membership_type__gte=Membership.MEMBERSHIP_TYPE_MANAGER)
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


@post_save_task()
def create_accepted_invitation_member_activity(new_membership_pk):
    new_membership = Membership.objects.get(pk=new_membership_pk)

    managers_filter = Q(membership_type__gte=Membership.MEMBERSHIP_TYPE_MANAGER)
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


@emailing_task(post_save=True)
def send_message_notification_email(message_pk):
    message = SupportGroupMessage.objects.get(pk=message_pk)

    memberships = message.supportgroup.memberships.filter(
        membership_type__gte=message.required_membership_type
    )
    recipients = Person.objects.filter(
        id__in=memberships.values_list("person_id", flat=True)
    )
    recipients_id = [recipient.id for recipient in recipients]

    recipients = Person.objects.exclude(id=message.author.id).filter(
        id__in=recipients_id,
        notification_subscriptions__membership__supportgroup=message.supportgroup,
        notification_subscriptions__type=Subscription.SUBSCRIPTION_EMAIL,
        notification_subscriptions__activity_type=Activity.TYPE_NEW_MESSAGE,
    )

    if len(recipients) == 0:
        return

    # Get membership to display author status
    membership_type = None
    membership = Membership.objects.filter(
        person=message.author, supportgroup=message.supportgroup
    )
    if membership.exists():
        membership_type = membership.first().membership_type
    author_status = genrer_membership(message.author.gender, membership_type)

    bindings = {
        "MESSAGE_HTML": format_html_join(
            "", "<p>{}</p>", ((p,) for p in message.text.split("\n"))
        ),
        "DISPLAY_NAME": message.author.display_name,
        "MESSAGE_LINK": front_url("user_message_details", kwargs={"pk": message_pk}),
        "AUTHOR_STATUS": format_html(
            '{} de <a href="{}">{}</a>',
            author_status,
            front_url("view_group", args=[message.supportgroup.pk]),
            message.supportgroup.name,
        ),
    }

    if message.subject:
        subject = message.subject
    else:
        subject = f"Nouveau message de {message.author.display_name}"
    subject = clean_subject_email(subject)

    send_mosaico_email(
        code="NEW_MESSAGE",
        subject=subject,
        from_email=settings.EMAIL_FROM,
        recipients=recipients,
        bindings=bindings,
    )


@emailing_task(post_save=True)
def send_comment_notification_email(comment_pk):
    comment = SupportGroupMessageComment.objects.select_related(
        "message__supportgroup", "author"
    ).get(pk=comment_pk)
    message = comment.message
    supportgroup = message.supportgroup
    author_membership = Membership.objects.filter(
        person=comment.author, supportgroup_id=message.supportgroup_id
    ).first()

    if message.required_membership_type > Membership.MEMBERSHIP_TYPE_FOLLOWER:
        # Private comment: send only to allowed membership and initial author
        recipients = filter_with_subscription(
            get_comment_recipients(comment),
            comment=comment,
            subscription_type=Subscription.SUBSCRIPTION_EMAIL,
            activity_type=Activity.TYPE_NEW_COMMENT_RESTRICTED,
        )
    else:
        # Public comment: send to all group members who ever commented
        recipients = filter_with_subscription(
            get_comment_participants(comment),
            comment=comment,
            subscription_type=Subscription.SUBSCRIPTION_EMAIL,
            activity_type=Activity.TYPE_NEW_COMMENT_RESTRICTED,
        )

    if len(recipients) == 0:
        return

    # TODO: utiliser les identifiants de message plutôt que le sujet pour permettre le regroupement
    subject = clean_subject_email(
        # on utilise le sujet du *message* initial pour pousser les clients mail à regrouper les différentes
        # notifications liées à un même message.
        message.subject
        if message.subject
        else f"Nouveau message de {comment.author.display_name}"
    )

    author_membership_type = genrer_membership(
        comment.author.gender,
        author_membership.membership_type if author_membership is not None else None,
    )

    bindings = {
        "MESSAGE_HTML": format_html_join(
            "", "<p>{}</p>", ((p,) for p in comment.text.split("\n"))
        ),
        "DISPLAY_NAME": comment.author.display_name,
        "MESSAGE_LINK": front_url(
            "view_group_message", args=[supportgroup.pk, comment_pk]
        ),
        "AUTHOR_STATUS": format_html(
            '{} de <a href="{}">{}</a>',
            author_membership_type,
            front_url("view_group", args=[supportgroup.pk]),
            supportgroup.name,
        ),
    }

    send_mosaico_email(
        code="NEW_MESSAGE",
        subject=subject,
        from_email=settings.EMAIL_FROM,
        recipients=recipients,
        bindings=bindings,
    )


@emailing_task(post_save=True)
def send_membership_transfer_email_notifications(
    transferer_pk, original_group_pk, target_group_pk, transferred_people_pks
):
    if len(transferred_people_pks) == 0:
        return

    try:
        transferer = Person.objects.get(pk=transferer_pk)
        transferred_people = Person.objects.filter(pk__in=transferred_people_pks)
    except Person.DoesNotExist:
        return

    try:
        original_group = SupportGroup.objects.get(pk=original_group_pk)
        target_group = SupportGroup.objects.get(pk=target_group_pk)
    except SupportGroup.DoesNotExist:
        return

    bindings = {
        "TRANSFERER_NAME": transferer.get_full_name(),
        "GROUP_SENDER": original_group.name,
        "GROUP_SENDER_URL": front_url("view_group", args=(original_group_pk,)),
        "GROUP_DESTINATION": target_group.name,
        "GROUP_DESTINATION_URL": front_url("view_group", args=(target_group_pk,)),
        "MANAGE_GROUP_LINK": front_url(
            "view_group_settings_members", args=(target_group_pk,)
        ),
        "MEMBER_LIST": [p.display_name for p in transferred_people],
        "MEMBER_COUNT": len(transferred_people_pks),
    }

    send_membership_transfer_sender_confirmation.delay(
        bindings, [m.pk for m in original_group.managers]
    )
    send_membership_transfer_receiver_confirmation.delay(
        bindings, [m.pk for m in target_group.managers]
    )
    for p in transferred_people:
        send_membership_transfer_alert.delay(bindings, p.pk)


@post_save_task()
def create_transfer_membership_activities(
    original_group_pk, target_group_pk, transferred_people_pks
):
    if len(transferred_people_pks) == 0:
        return

    try:
        transferred_people = Person.objects.filter(pk__in=transferred_people_pks)
    except Person.DoesNotExist:
        return

    try:
        original_group = SupportGroup.objects.get(pk=original_group_pk)
        target_group = SupportGroup.objects.get(pk=target_group_pk)
    except SupportGroup.DoesNotExist:
        return

    Activity.objects.bulk_create(
        [
            Activity(
                type=Activity.TYPE_TRANSFERRED_GROUP_MEMBER,
                status=Activity.STATUS_UNDISPLAYED,
                recipient=r,
                supportgroup=target_group,
                meta={"oldGroup": original_group.name},
            )
            for r in transferred_people
        ],
        send_post_save_signal=True,
    )

    # Create activities for target group managers
    managers_filter = Q(membership_type__gte=Membership.MEMBERSHIP_TYPE_MANAGER)
    managing_membership = target_group.memberships.filter(managers_filter)
    managing_membership_recipients = [
        membership.person for membership in managing_membership
    ]
    Activity.objects.bulk_create(
        [
            Activity(
                type=Activity.TYPE_NEW_MEMBERS_THROUGH_TRANSFER,
                recipient=r,
                supportgroup=target_group,
                meta={
                    "oldGroup": original_group.name,
                    "transferredMemberships": len(transferred_people),
                },
            )
            for r in managing_membership_recipients
        ],
        send_post_save_signal=True,
    )


@post_save_task()
def subscribe_supportgroup_referents_to_main_newsletters(supportgroup_pk):
    supportgroup = SupportGroup.objects.get(pk=supportgroup_pk)
    recipients = supportgroup.referents
    for referent in recipients:
        if not referent.subscribed:
            referent.subscribed = True
            referent.save()


@emailing_task()
def send_newly_certified_group_notifications(supportgroup_pk):
    supportgroup = SupportGroup.objects.get(pk=supportgroup_pk)
    recipients = supportgroup.referents
    send_template_email(
        template_name="groups/email/newly_certified_group_email.html",
        from_email=settings.EMAIL_FROM,
        bindings={
            "group": supportgroup,
            "url": {
                "group_page": front_url(
                    "view_group",
                    args=[supportgroup_pk],
                    absolute=True,
                ),
                "view_group_settings_materiel": front_url(
                    "view_group_settings_materiel",
                    args=[supportgroup_pk],
                    absolute=True,
                ),
                "contribution_amount": front_url(
                    "supportgroup_contribution",
                    kwargs={"pk": supportgroup.pk},
                    absolute=True,
                ),
                "create_event": front_url(
                    "create_event", absolute=True, query={"group": supportgroup_pk}
                ),
                "group_map_page": front_url("group_map_page", absolute=True),
            },
        },
        recipients=[*recipients, settings.EMAIL_SUPPORT],
    )


@emailing_task()
def send_uncertifiable_group_warning(supportgroup_pk, expiration_in_days):
    supportgroup = SupportGroup.objects.get(pk=supportgroup_pk)
    recipients = supportgroup.managers
    certification_criteria = check_certification_criteria(supportgroup)
    # Double-check if any criterium is unmatched to avoid false positives
    if all(certification_criteria.values()):
        raise Exception(
            f"False positive: uncertifiable group warning scheduled for group #{supportgroup_pk}"
        )
    Activity.objects.bulk_create(
        [
            Activity(
                type=Activity.TYPE_UNCERTIFIABLE_GROUP_WARNING,
                recipient=r,
                supportgroup_id=supportgroup_pk,
                meta={
                    "criteria": certification_criteria,
                    "expiration": expiration_in_days,
                },
            )
            for r in recipients
        ],
        send_post_save_signal=True,
    )
    send_template_email(
        template_name="groups/email/uncertifiable_group_warning.html",
        from_email=settings.EMAIL_FROM,
        bindings={
            "group": supportgroup,
            "expiration_in_days": expiration_in_days,
            "certification_criteria": certification_criteria,
        },
        recipients=recipients,
    )
    with reversion.create_revision():
        reversion.set_comment(
            "Avertissement envoyé pour non-respect des critères de certification"
        )
        reversion.set_date_created(timezone.now())
        reversion.add_to_revision(supportgroup)


@emailing_task()
def send_uncertifiable_group_list(supportgroup_pks, expiration_in_days):
    supportgroups = SupportGroup.objects.filter(pk__in=supportgroup_pks)
    send_template_email(
        template_name="groups/email/uncertifiable_group_list.html",
        from_email=settings.EMAIL_FROM,
        bindings={"groups": supportgroups, "expiration_in_days": expiration_in_days},
        recipients=[settings.EMAIL_SUPPORT],
    )


@emailing_task()
def send_uncertified_group_notifications(supportgroup_pk):
    supportgroup = SupportGroup.objects.get(pk=supportgroup_pk)
    recipients = supportgroup.referents
    send_template_email(
        template_name="groups/email/uncertified_group_email.html",
        from_email=settings.EMAIL_FROM,
        bindings={"group": supportgroup},
        recipients=[*recipients, settings.EMAIL_SUPPORT],
    )
