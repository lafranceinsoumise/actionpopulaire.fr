from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import Client
from ..authentication.models import Role


@receiver(pre_save, sender=Client, dispatch_uid="client_ensure_has_role")
def ensure_has_role(sender, instance, raw, **kwargs):
    if not raw and instance.role_id is None:
        role = Role.objects.create(type=Role.CLIENT_ROLE)
        instance.role = role
