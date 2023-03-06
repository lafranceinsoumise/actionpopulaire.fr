from agir.groups.tasks import (
    send_membership_transfer_email_notifications,
    create_transfer_membership_activities,
)


def schedule_membership_transfer_tasks(transfer_operation):
    transferred_people_pks = list(
        transfer_operation.members.values_list("pk", flat=True)
    )

    if len(transferred_people_pks) == 0:
        return

    send_membership_transfer_email_notifications.delay(
        transfer_operation.manager_id,
        transfer_operation.former_group_id,
        transfer_operation.new_group_id,
        transferred_people_pks,
    )

    create_transfer_membership_activities.delay(
        transfer_operation.former_group_id,
        transfer_operation.new_group_id,
        transferred_people_pks,
    )
