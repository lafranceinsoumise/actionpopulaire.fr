from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import Person


@receiver(post_delete, sender=Person, dispatch_uid="person_delete_role")
def delete_role(sender, instance, **kwargs):
    try:
        if instance.role is not None:
            instance.role.delete()
    except ObjectDoesNotExist:
        pass
