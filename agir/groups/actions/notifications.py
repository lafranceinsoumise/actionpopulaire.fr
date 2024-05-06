from functools import partial

from django.db import transaction
from django.db.models import Exists, OuterRef, Q
from django.db.models.functions import Coalesce

from agir.activity.models import Activity
from agir.groups.models import SupportGroup, Membership
from agir.groups.tasks import (
    GROUP_MEMBERSHIP_LIMIT_NOTIFICATION_STEPS,
    send_joined_notification_email,
    send_alert_capacity_email,
    send_message_notification_email,
    send_comment_notification_email,
)
from agir.msgs.actions import (
    get_comment_recipients,
    filter_with_subscription,
    get_comment_participants,
    get_comment_other_recipients,
)
from agir.msgs.models import SupportGroupMessageRecipient, SupportGroupMessageComment
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

    send_joined_notification_email.delay(membership.pk)


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


# Group comment with required membership type
@transaction.atomic()
def new_comment_restricted_notifications(comment):
    """Group comment with required membership type"""
    message_initial = comment.message
    muted_recipients = Person.objects.filter(
        read_messages__message=message_initial, read_messages__muted=True
    ).values("id")
    allowed_memberships = message_initial.supportgroup.memberships.filter(
        membership_type__gte=message_initial.required_membership_type
    )
    recipients_id = allowed_memberships.exclude(
        person_id__in=muted_recipients
    ).values_list("person_id", flat=True)
    recipients_id = set(list(recipients_id) + [message_initial.author_id])

    # Get only recipients with notification allowed
    recipients = Person.objects.annotate(
        muted=Exists(
            SupportGroupMessageRecipient.objects.filter(
                person_id=OuterRef("id"), message_id=comment.message_id, muted=True
            )
        )
    ).filter(
        muted=False,
        memberships__supportgroup_id=message_initial.supportgroup_id,
        membership_type__gte=message_initial.required_membership_type,
        notificationsubscriptions__membership=message_initial.supportgroup,
    )

    recipients_allowed_notif = message_initial.supportgroup.members.filter(
        notification_subscriptions__membership__supportgroup=message_initial.supportgroup,
        notification_subscriptions__person__in=recipients_id,
        notification_subscriptions__type=Subscription.SUBSCRIPTION_PUSH,
        notification_subscriptions__activity_type=Activity.TYPE_NEW_COMMENT_RESTRICTED,
    )

    send_comment_notification_email.delay(comment.pk)

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


def make_comment_notification_activity(comment, recipient):
    if recipient.is_comment_author or comment.message.author_id == recipient.id:
        activity_type = Activity.TYPE_NEW_COMMENT_RESTRICTED
    else:
        activity_type = Activity.TYPE_NEW_COMMENT

    return Activity(
        individual=comment.author,
        supportgroup=comment.message.supportgroup,
        type=activity_type,
        recipient=recipient,
        status=Activity.STATUS_UNDISPLAYED,
        meta={
            "message": str(comment.message_id),
            "comment": str(comment.pk),
        },
    )


@transaction.atomic()
def new_comment_notifications(comment: SupportGroupMessageComment):
    message_initial = comment.message

    if message_initial.required_membership_type > Membership.MEMBERSHIP_TYPE_FOLLOWER:
        # pour un message de pour lequel le membership est limité, on considère que tous les
        # participants font partie de la conversation
        restricted_recipients = filter_with_subscription(
            get_comment_recipients(comment),
            comment=comment,
            subscription_type=Subscription.SUBSCRIPTION_PUSH,
            activity_type=Activity.TYPE_NEW_COMMENT_RESTRICTED,
        )

        other_recipients = []
    else:
        # sinon, on considère comme participants à la conversation l'auteur du message et tous les
        # auteurs de commentaires
        restricted_recipients = filter_with_subscription(
            get_comment_participants(comment),
            comment=comment,
            subscription_type=Subscription.SUBSCRIPTION_PUSH,
            activity_type=Activity.TYPE_NEW_COMMENT_RESTRICTED,
        )

        other_recipients = filter_with_subscription(
            get_comment_other_recipients(comment),
            comment=comment,
            subscription_type=Subscription.SUBSCRIPTION_PUSH,
            activity_type=Activity.TYPE_NEW_COMMENT,
        )

    restricted_activities = [
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
        for r in restricted_recipients
    ]
    other_activities = [
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
    ]

    send_comment_notification_email.delay(comment.pk)

    Activity.objects.bulk_create(
        restricted_activities + other_activities,
        send_post_save_signal=True,
    )


@transaction.atomic()
def member_to_follower_notification(membership):
    Activity.objects.create(
        type=Activity.TYPE_MEMBER_STATUS_CHANGED,
        recipient=membership.person,
        supportgroup=membership.supportgroup,
    )
