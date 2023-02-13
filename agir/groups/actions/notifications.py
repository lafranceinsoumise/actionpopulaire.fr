from functools import partial

from django.db import transaction

from agir.activity.models import Activity
from agir.groups.models import SupportGroup, Membership
from agir.groups.tasks import (
    GROUP_MEMBERSHIP_LIMIT_NOTIFICATION_STEPS,
    send_joined_notification_email,
    send_alert_capacity_email,
    send_message_notification_email,
    send_comment_notification_email,
)
from agir.notifications.models import Subscription
from agir.people.models import Person


@transaction.atomic()
def someone_joined_notification(membership, membership_count=1):
    recipients = membership.supportgroup.managers
    activity_type = (
        Activity.TYPE_NEW_MEMBER
        if membership.is_active_member
        else Activity.TYPE_NEW_FOLLOWER
    )
    Activity.objects.bulk_create(
        [
            Activity(
                type=activity_type,
                recipient=r,
                supportgroup=membership.supportgroup,
                individual=membership.person,
                meta={"email": membership.person.display_email},
            )
            for r in recipients
        ],
        send_post_save_signal=True,
    )

    if not membership.is_active_member:
        return

    membership_limit_notication_steps = [
        membership.supportgroup.MEMBERSHIP_LIMIT + step
        for step in GROUP_MEMBERSHIP_LIMIT_NOTIFICATION_STEPS
        if membership.supportgroup.MEMBERSHIP_LIMIT + step > 0
    ]

    if (
        membership.supportgroup.type == SupportGroup.TYPE_LOCAL_GROUP
        and membership_count in membership_limit_notication_steps
    ):
        current_membership_limit_notification_step = (
            membership_limit_notication_steps.index(membership_count)
        )
        Activity.objects.bulk_create(
            [
                Activity(
                    type=Activity.TYPE_GROUP_MEMBERSHIP_LIMIT_REMINDER,
                    recipient=r,
                    supportgroup=membership.supportgroup,
                    status=Activity.STATUS_UNDISPLAYED,
                    meta={
                        "membershipLimit": membership.supportgroup.MEMBERSHIP_LIMIT,
                        "membershipCount": membership_count,
                        "membershipLimitNotificationStep": current_membership_limit_notification_step,
                    },
                )
                for r in recipients
            ],
            send_post_save_signal=True,
        )
    if (
        membership.supportgroup.type == SupportGroup.TYPE_LOCAL_GROUP
        and membership_count
        in [
            21,
            # 30, (disabled until further notice)
        ]
    ):
        transaction.on_commit(
            partial(
                send_alert_capacity_email.delay,
                membership.supportgroup.pk,
                membership_count,
            )
        )

    transaction.on_commit(partial(send_joined_notification_email.delay, membership.pk))


@transaction.atomic()
def new_message_notifications(message):
    memberships = message.supportgroup.memberships.filter(
        membership_type__gte=message.required_membership_type
    )
    recipients = Person.objects.filter(
        id__in=memberships.values_list("person_id", flat=True)
    )

    Activity.objects.bulk_create(
        [
            Activity(
                individual=message.author,
                supportgroup=message.supportgroup,
                type=Activity.TYPE_NEW_MESSAGE,
                recipient=r,
                status=Activity.STATUS_UNDISPLAYED,
                meta={
                    "message": str(message.pk),
                },
            )
            for r in recipients
            if r.pk != message.author.pk
        ],
        send_post_save_signal=True,
    )

    send_message_notification_email.delay(message.pk)


@transaction.atomic()
# Group comment with required membership type
def new_comment_restricted_notifications(comment):
    message_initial = comment.message
    muted_recipients = message_initial.recipient_mutedlist.values("id")
    allowed_memberships = message_initial.supportgroup.memberships.filter(
        membership_type__gte=message_initial.required_membership_type
    )
    recipients_id = allowed_memberships.exclude(
        person_id__in=muted_recipients
    ).values_list("person_id", flat=True)
    recipients_id = set(list(recipients_id) + [message_initial.author_id])

    # Get only recipients with notification allowed
    recipients_allowed_notif = message_initial.supportgroup.members.filter(
        notification_subscriptions__membership__supportgroup=message_initial.supportgroup,
        notification_subscriptions__person__in=recipients_id,
        notification_subscriptions__type=Subscription.SUBSCRIPTION_PUSH,
        notification_subscriptions__activity_type=Activity.TYPE_NEW_COMMENT_RESTRICTED,
    )

    Activity.objects.bulk_create(
        [
            Activity(
                individual=comment.author,
                supportgroup=message_initial.supportgroup,
                type=Activity.TYPE_NEW_COMMENT_RESTRICTED,
                recipient=r,
                status=Activity.STATUS_UNDISPLAYED,
                meta={
                    "message": str(message_initial.pk),
                    "comment": str(comment.pk),
                },
            )
            for r in recipients_allowed_notif
            if r.pk != comment.author.pk
        ],
        send_post_save_signal=True,
    )

    send_comment_notification_email.delay(comment.pk)


@transaction.atomic()
def new_comment_notifications(comment):
    if comment.message.required_membership_type > Membership.MEMBERSHIP_TYPE_FOLLOWER:
        new_comment_restricted_notifications(comment)
        return

    message_initial = comment.message
    muted_recipients = message_initial.recipient_mutedlist.values("id")
    comment_authors = list(message_initial.comments.values_list("author_id", flat=True))
    comment_authors = set(comment_authors + [message_initial.author_id])

    participant_recipients = message_initial.supportgroup.members.exclude(
        id__in=muted_recipients
    ).filter(
        notification_subscriptions__membership__supportgroup=message_initial.supportgroup,
        notification_subscriptions__person__in=comment_authors,
        notification_subscriptions__type=Subscription.SUBSCRIPTION_PUSH,
        notification_subscriptions__activity_type=Activity.TYPE_NEW_COMMENT_RESTRICTED,
    )

    Activity.objects.bulk_create(
        [
            Activity(
                individual=comment.author,
                supportgroup=message_initial.supportgroup,
                type=Activity.TYPE_NEW_COMMENT_RESTRICTED,
                recipient=r,
                status=Activity.STATUS_UNDISPLAYED,
                meta={
                    "message": str(message_initial.pk),
                    "comment": str(comment.pk),
                },
            )
            for r in participant_recipients
            if r.pk != comment.author.pk
        ],
        send_post_save_signal=True,
    )

    other_recipients = (
        message_initial.supportgroup.members.exclude(
            id__in=participant_recipients.values_list("id", flat=True)
        )
        .filter(
            notification_subscriptions__membership__supportgroup=message_initial.supportgroup,
            notification_subscriptions__type=Subscription.SUBSCRIPTION_PUSH,
            notification_subscriptions__activity_type=Activity.TYPE_NEW_COMMENT,
        )
        .exclude(id__in=muted_recipients)
    )

    Activity.objects.bulk_create(
        [
            Activity(
                individual=comment.author,
                supportgroup=message_initial.supportgroup,
                type=Activity.TYPE_NEW_COMMENT,
                recipient=r,
                status=Activity.STATUS_UNDISPLAYED,
                meta={
                    "message": str(message_initial.pk),
                    "comment": str(comment.pk),
                },
            )
            for r in other_recipients
            if r.pk != comment.author.pk
        ],
        send_post_save_signal=True,
    )

    send_comment_notification_email.delay(comment.pk)


@transaction.atomic()
def member_to_follower_notification(membership):
    Activity.objects.create(
        type=Activity.TYPE_MEMBER_STATUS_CHANGED,
        recipient=membership.person,
        supportgroup=membership.supportgroup,
    )
