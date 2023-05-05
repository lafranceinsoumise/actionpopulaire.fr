from django.conf import settings
from django.db import models

from agir.groups.models import SupportGroup, SupportGroupQuerySet
from agir.groups.utils.certification import (
    add_certification_criteria_to_queryset,
    check_certification_criteria,
)


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


class UncertifiableGroupManager(models.Manager.from_queryset(SupportGroupQuerySet)):
    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .active()
            .certified()
            .filter(type=SupportGroup.TYPE_LOCAL_GROUP)
        )
        return add_certification_criteria_to_queryset(qs).filter(certifiable=False)


class UncertifiableGroup(SupportGroup):
    objects = UncertifiableGroupManager()

    class Meta:
        default_permissions = ("view", "change")
        verbose_name = "Groupe décertifiable"
        verbose_name_plural = "Groupes décertifiables"
        proxy = True
