from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Person
from ..groups.models import Membership


@receiver(post_delete, sender=Person, dispatch_uid="person_delete_role")
def delete_role(sender, instance, **kwargs):
    try:
        if instance.role is not None:
            instance.role.delete()
    except ObjectDoesNotExist:
        pass


@receiver(
    post_save, sender=Membership, dispatch_uid="membership_person_political_support"
)
def membership_person_political_support(sender, instance, **kwargs):
    if (
        instance.membership_type >= Membership.MEMBERSHIP_TYPE_MEMBER
        and not instance.person.is_political_support
    ):
        instance.person.is_political_support = True
        instance.person.save()
