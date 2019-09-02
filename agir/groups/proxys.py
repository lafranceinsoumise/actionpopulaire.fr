from django.db import models

from agir.groups.models import SupportGroup


class ThematicGroupManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type=SupportGroup.TYPE_THEMATIC)


class ThematicGroup(SupportGroup):
    objects = ThematicGroupManager()

    class Meta:
        default_permissions = ("view", "change")
        verbose_name = "Groupe thématique"
        verbose_name_plural = "Groupes thématiques"
        proxy = True
