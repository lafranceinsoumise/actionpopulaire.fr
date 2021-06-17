from functools import partial

from django.db import transaction

from agir.activity.models import Activity
from agir.groups.tasks import (
    GROUP_MEMBERSHIP_LIMIT_NOTIFICATION_STEPS,
    send_joined_notification_email,
    send_alert_capacity_email,
    send_message_notification_email,
    send_comment_notification_email,
)
from agir.notifications.types import SubscriptionType


@transaction.atomic()
def someone_joined_notification(membership, membership_count=1):
    recipients = membership.supportgroup.managers

    Activity.objects.bulk_create(
        [
            Activity(
                type=SubscriptionType.TYPE_NEW_MEMBER,
                recipient=r,
                supportgroup=membership.supportgroup,
                individual=membership.person,
                meta={"email": membership.person.email},
            )
            for r in recipients
        ],
        send_post_save_signal=True,
    )

    membership_limit_notication_steps = [
        membership.supportgroup.MEMBERSHIP_LIMIT + step
        for step in GROUP_MEMBERSHIP_LIMIT_NOTIFICATION_STEPS
        if membership.supportgroup.MEMBERSHIP_LIMIT + step > 0
    ]

    if (
        membership.supportgroup.is_2022
        and membership_count in membership_limit_notication_steps
    ):
        current_membership_limit_notification_step = membership_limit_notication_steps.index(
            membership_count
        )
        Activity.objects.bulk_create(
            [
                Activity(
                    type=SubscriptionType.TYPE_GROUP_MEMBERSHIP_LIMIT_REMINDER,
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
    if membership.supportgroup.is_2022 and membership_count in [21, 30]:
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
    recipients = message.supportgroup.members.all()
    Activity.objects.bulk_create(
        [
            Activity(
                individual=message.author,
                supportgroup=message.supportgroup,
                type=SubscriptionType.TYPE_NEW_MESSAGE,
                recipient=r,
                status=Activity.STATUS_UNDISPLAYED,
                meta={"message": str(message.pk),},
            )
            for r in recipients
            if r.pk != message.author.pk
        ],
        send_post_save_signal=True,
    )

    send_message_notification_email.delay(message.pk)


@transaction.atomic()
def new_comment_notifications(comment):
    recipients = [comment.message.author] + [
        comment.author for comment in comment.message.comments.all()
    ]
    Activity.objects.bulk_create(
        [
            Activity(
                individual=comment.author,
                supportgroup=comment.message.supportgroup,
                type=SubscriptionType.TYPE_NEW_COMMENT,
                recipient=r,
                status=Activity.STATUS_UNDISPLAYED,
                meta={"message": str(comment.message.pk), "comment": str(comment.pk),},
            )
            for r in recipients
            if r.pk != comment.author.pk
        ],
        send_post_save_signal=True,
    )

    send_comment_notification_email.delay(comment.pk)
