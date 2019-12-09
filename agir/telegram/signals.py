from django.db.models.signals import post_save
from django.dispatch import receiver

from agir.telegram import tasks
from agir.telegram.models import TelegramGroup


@receiver(post_save, sender=TelegramGroup, dispatch_uid="update_members")
def update_members(sender, instance, **kwargs):
    tasks.update_telegram_groups.delay(instance.pk)
