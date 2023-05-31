from functools import partial

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Event, RSVP, IdentifiedGuest
from .tasks import (
    copier_rsvp_vers_feuille_externe,
    copier_identified_guest_vers_feuille_externe,
)


def copier_participant_feuille_externe(instance, sheet):
    if not sheet:
        return

    task = None

    if isinstance(instance, RSVP):
        task = copier_rsvp_vers_feuille_externe.delay

    if isinstance(instance, IdentifiedGuest):
        task = copier_identified_guest_vers_feuille_externe.delay

    if not task:
        return

    transaction.on_commit(partial(task, instance.pk))


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
