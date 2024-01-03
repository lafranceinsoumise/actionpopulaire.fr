from django.core.exceptions import ObjectDoesNotExist
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


def add_organizer_group(event, group, as_person=None, exclude_organizer=None):
    if as_person is not None:
        organizers = [as_person]
    else:
        # Defaults to group referents (and fallback to managers) if no organizer person is specified
        organizers = group.referents or group.managers

    if exclude_organizer is not None:
        organizers = [
            organizer for organizer in organizers if organizer != exclude_organizer
        ]

    if not organizers:
        return

    return models.OrganizerConfig.objects.bulk_create(
        [
            models.OrganizerConfig(
                event=event,
                as_group=group,
                person=organizer,
            )
            for organizer in organizers
        ],
        ignore_conflicts=True,
    )


def accept_group_organization_invitation(invitation, person):
    try:
        invitation.event.organizers_groups.get(pk=invitation.group_id)
        raise CoorganizationResponseException(
            "Votre groupe a déjà accepté de coorganiser cet événement"
        )
    except ObjectDoesNotExist:
        pass

    add_organizer_group(invitation.event, invitation.group, as_person=person)
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
        created = accept_group_organization_invitation(invitation, person)
        Activity.objects.filter(
            event=invitation.event,
            supportgroup=invitation.group,
            type=Activity.TYPE_GROUP_COORGANIZATION_INVITE,
        ).update(status=Activity.STATUS_INTERACTED, meta={})

        return created
