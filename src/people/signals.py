from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver
from django.conf import settings

from lib.mailtrain import delete_person
from people import tasks
from .models import Person, PersonEmail
from authentication.models import Role


@receiver(pre_save, sender=Person, dispatch_uid="person_ensure_has_role")
def ensure_has_role(sender, instance, raw, **kwargs):
    if not raw and instance.role_id is None:
        role = Role.objects.create(type=Role.PERSON_ROLE)
        instance.role = role


@receiver(post_save, sender=Person, dispatch_uid="person_update_mailtrain")
def update_mailtrain(sender, instance, raw, **kwargs):
    if settings.MAILTRAIN_DISABLE:
        return

    tasks.update_mailtrain.delay(instance.id)


@receiver(pre_delete, sender=Person, dispatch_uid="person_delete_mailtrain")
def delete_mailtrain(sender, instance, **kwargs):
    delete_person(instance)


@receiver(pre_delete, sender=PersonEmail, dispatch_uid="personemail_delete_mailtrain")
def delete_email_person(sender, instance, **kwargs):
    if settings.MAILTRAIN_DISABLE:
        return

    tasks.update_mailtrain.delay(instance.person_id)
