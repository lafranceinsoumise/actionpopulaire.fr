from django.db.models import Q
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe

from agir.activity.models import Activity
from agir.groups.models import SupportGroup, Membership
from agir.groups.tasks import (
    send_membership_transfer_sender_confirmation,
    send_membership_transfer_receiver_confirmation,
    send_membership_transfer_alert,
)
from agir.lib.utils import front_url
from agir.people.models import Person


def send_membership_transfer_email_notifications(
    transferer_pk, original_group_pk, target_group_pk, transferred_people_pks
):
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
        "MEMBER_LIST": format_html_join(
            mark_safe("<br>"), "{}", [p.get_full_name() for p in transferred_people]
        ),
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


def create_transfer_membership_activities(
    original_group, target_group, transferred_people
):
    if len(transferred_people) == 0:
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
