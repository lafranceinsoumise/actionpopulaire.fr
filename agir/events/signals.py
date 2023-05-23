from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Event, RSVP, IdentifiedGuest
from .tasks import (
    copier_rsvp_vers_feuille_externe,
    copier_identified_guest_vers_feuille_externe,
)


@receiver(post_save, sender=RSVP, dispatch_uid="copier_rsvp_feuille_externe")
def signal_copier_rsvp_feuille_externe(sender, instance, **kwargs):
    if instance.event.lien_feuille_externe:
        copier_rsvp_vers_feuille_externe.delay(instance.pk)


@receiver(
    post_save,
    sender=IdentifiedGuest,
    dispatch_uid="copier_identified_guest_feuille_externe",
)
def signal_copier_identified_guest_feuille_externe(sender, instance, **kwargs):
    sheet_url = Event.objects.values("lien_feuille_externe").get(
        rsvps__id=instance.rsvp_id
    )["lien_feuille_externe"]
    if sheet_url:
        copier_identified_guest_vers_feuille_externe.delay(instance.pk)
