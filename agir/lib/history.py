from itertools import chain

from django.db import models
from reversion.models import Version


class HistoryMixin:
    DIFFED_FIELDS = []

    @classmethod
    def get_history_step(cls, old, new, **kwargs):
        old_obj = old._object_version.object if old is not None else None
        new_obj = new._object_version.object
        revision = new.revision

        step = {
            "id": new.pk,
            "title": "Modification" if old else "Création",
            "modified": getattr(new_obj, "modified", revision.date_created),
            "comment": revision.get_comment(),
            "diff": cls.get_diff(old_obj, new_obj),
            "person": revision.user.person if revision.user else None,
        }

        return step

    @classmethod
    def get_field_labels(cls, fields):
        return [str(cls._meta.get_field(field).verbose_name) for field in fields]

    @classmethod
    def get_diff(cls, before, after):
        diff = []

        if not before:
            return diff

        for field in cls.DIFFED_FIELDS:
            if not hasattr(after, field) or not hasattr(before, field):
                continue
            old = getattr(before, field, None)
            new = getattr(after, field, None)

            if isinstance(new, (models.QuerySet, models.Manager)):
                old = list(old.order_by("pk").values_list("pk", flat=True))
                new = list(new.order_by("pk").values_list("pk", flat=True))

            if old != new:
                diff.append(field)

        return cls.get_field_labels(diff)

    def get_history(self, **kwargs):
        versions = list(
            Version.objects.get_for_object(self)
            .order_by("pk")
            .select_related("revision__user__person")
        )

        steps = [
            self.get_history_step(previous_version, version)
            for previous_version, version in zip(chain([None], versions[:-1]), versions)
        ]

        # Reverse the list to have the most recent items first
        return steps[::-1]
