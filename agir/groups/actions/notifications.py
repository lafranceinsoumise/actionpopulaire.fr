from functools import partial

from django.db import transaction

from agir.activity.models import Activity
from agir.groups.tasks import (
    GROUP_MEMBERSHIP_LIMIT_NOTIFICATION_STEPS,
    send_joined_notification_email,
    send_alert_capacity_email,
)


@transaction.atomic()
def someone_joined_notification(membership, membership_count=1):
    recipients = membership.supportgroup.managers

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

    membership_limit_notication_steps = [
        membership.supportgroup.MEMBERSHIP_LIMIT + step
        for step in GROUP_MEMBERSHIP_LIMIT_NOTIFICATION_STEPS
        if membership.supportgroup.MEMBERSHIP_LIMIT + step > 0
    ]

    if membership_count in membership_limit_notication_steps:
        current_membership_limit_notification_step = membership_limit_notication_steps.index(
            membership_count
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
            ]
        )
    if membership_count in [21, 30]:
        transaction.on_commit(
            partial(send_alert_capacity_email.delay, membership.pk, membership_count)
        )

    transaction.on_commit(partial(send_joined_notification_email.delay, membership.pk))
