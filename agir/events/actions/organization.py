from django.db import transaction

from agir.activity.models import Activity
from agir.events import models
from agir.events import tasks
from agir.groups import tasks as group_tasks


class CoorganizationResponseException(Exception):
    pass


def schedule_new_organizer_group_notifications(invitation):
    # Notify the event organizers
    tasks.send_accepted_group_coorganization_invitation_notification.delay(
        invitation.id
    )
    # Notify the group members
    group_tasks.send_new_group_event_email.delay(
        invitation.group_id, invitation.event_id
    )
    group_tasks.notify_new_group_event.delay(invitation.group_id, invitation.event_id)


def add_organizer_group(invitation, person):
    _, created = models.OrganizerConfig.objects.get_or_create(
        event=invitation.event,
        as_group=invitation.group,
        defaults={"person": person, "is_creator": False},
    )
    if not created:
        raise CoorganizationResponseException(
            "Votre groupe a déjà accepté de coorganiser cet événement"
        )

    schedule_new_organizer_group_notifications(invitation)

    return True


def respond_to_coorganization_invitation(invitation, person, accepted=True):
    with transaction.atomic():
        invitation.person_recipient = person

        if not accepted and invitation.status != models.Invitation.STATUS_PENDING:
            raise CoorganizationResponseException(
                "Il n'est plus possible de répondre à l'invitation de coorganisation",
            )

        if invitation.event.is_past():
            raise CoorganizationResponseException(
                "Il n'est plus possible de répondre à l'invitation de coorganisation",
            )

        if not accepted:
            invitation.status = models.Invitation.STATUS_REFUSED
            invitation.save()
            tasks.send_refused_group_coorganization_invitation_notification.delay(
                invitation.id
            )
            return

        invitation.status = models.Invitation.STATUS_ACCEPTED
        invitation.save()
        created = add_organizer_group(invitation, person)
        Activity.objects.filter(
            event=invitation.event,
            supportgroup=invitation.group,
            type=Activity.TYPE_GROUP_COORGANIZATION_INVITE,
        ).update(status=Activity.STATUS_INTERACTED, meta={})

        return created
