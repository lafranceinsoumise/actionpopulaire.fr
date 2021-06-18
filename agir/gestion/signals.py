from django.contrib.admin.options import get_content_type_for_model
from django.db.models.signals import pre_delete, post_save

from agir.gestion.models.common import InstanceCherchable, ModeleGestionMixin


def creer_ou_mettre_a_jour_recherche(sender, instance, raw, **kwargs):
    if raw:
        return

    content_type = get_content_type_for_model(instance)
    search_vector_def = instance.search_vector()

    InstanceCherchable.objects.update_or_create(
        content_type=content_type,
        object_id=instance.pk,
        defaults={
            "recherche": sender.objects.values(v=search_vector_def).filter(
                pk=instance.pk
            )
        },
    )


for klass in ModeleGestionMixin.__subclasses__():
    post_save.connect(creer_ou_mettre_a_jour_recherche, sender=klass)
