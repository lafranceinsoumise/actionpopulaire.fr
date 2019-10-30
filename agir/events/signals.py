from django.db.models.signals import pre_save
from django.dispatch import receiver

from agir.events.models import Event
from agir.lib.utils import front_url
from agir.notifications.models import Notification


@receiver(pre_save, sender=Event, dispatch_uid="delete_event_notification")
def delete_event_notification(sender, instance, raw, **kwargs):
    if instance.pk is None:
        return
    if sender.visibility != Event.VISIBILITY_PUBLIC:
        Notification.objects.filter(
            link=front_url("view_event", args=[instance.pk])
        ).delete()
