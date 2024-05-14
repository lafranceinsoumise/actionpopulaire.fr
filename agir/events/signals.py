from django.db.models import Exists, OuterRef
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from .models import RSVP, IdentifiedGuest, OrganizerConfig
from .tasks import (
    copier_rsvp_vers_feuille_externe,
    copier_identified_guest_vers_feuille_externe,
)
from ..people.models import Person


def copier_participant_feuille_externe(instance, sheet):
    if not sheet:
        return

    task = None

    if isinstance(instance, RSVP):
        task = copier_rsvp_vers_feuille_externe

    if isinstance(instance, IdentifiedGuest):
        task = copier_identified_guest_vers_feuille_externe

    if not task:
        return

    task.delay(instance.pk)


@receiver(post_save, sender=RSVP, dispatch_uid="copier_rsvp_feuille_externe")
def signal_copier_rsvp_feuille_externe(sender, instance, **kwargs):
    copier_participant_feuille_externe(
        instance,
        instance.event.lien_feuille_externe,
    )


@receiver(
    post_save,
    sender=IdentifiedGuest,
    dispatch_uid="copier_identified_guest_feuille_externe",
)
def signal_copier_identified_guest_feuille_externe(sender, instance, **kwargs):
    copier_participant_feuille_externe(
        instance, instance.rsvp.event.lien_feuille_externe
    )


@receiver(
    pre_delete,
    sender=Person,
    dispatch_uid="transfer_last_group_organizer_config_to_group_referents",
)
def signal_transfer_group_organizer_config_to_group_referents(
    sender, instance, **kwargs
):
    """
    Signal to create new organizer config instances for a group when the as_group is set and the existing organizer
    config is the last one for the group for the event.
    """

    organizer_configs = (
        instance.organizer_configs
        # Only create a new organizer config if the existing one is for a group
        .filter(as_group__isnull=False)
        # Only create a new organizer config if the existing one is the only one for the group
        .annotate(
            is_last=~Exists(
                OrganizerConfig.objects.exclude(person=instance).filter(
                    event_id=OuterRef("event_id"), as_group_id=OuterRef("as_group_id")
                )
            )
        )
        .filter(is_last=True)
        .select_related("event", "as_group")
    )

    for organizer_config in organizer_configs:
        organizer_config.event.add_organizer_group(
            organizer_config.as_group, exclude_organizer=instance
        )
