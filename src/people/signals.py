from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import Person
from authentication.models import Role


@receiver(pre_save, sender=Person, dispatch_uid="ensure_has_role")
def ensure_has_role(sender, instance, raw, **kwargs):
    if not raw and instance.role_id is None:
        role = Role.objects.create(type=Role.PERSON_ROLE)
        instance.role = role
