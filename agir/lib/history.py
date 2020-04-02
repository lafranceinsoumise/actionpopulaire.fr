from itertools import chain
from typing import Optional

from reversion.models import Version


class HistoryMixin:
    DIFFED_FIELDS = []

    @classmethod
    def get_history_step(cls, old: Optional[Version], new: Version, **kwargs):
        raise NotImplementedError("Cette méthode doit être implémentée")

    @classmethod
    def get_diff(cls, before, after):
        return [
            str(cls._meta.get_field(f).verbose_name)
            for f in cls.DIFFED_FIELDS
            if after.get(f) != before.get(f)
        ]

    def get_history(self, **kwargs):
        versions = list(
            Version.objects.get_for_object(self)
            .order_by("pk")
            .select_related("revision__user__person")
        )

        return [
            self.get_history_step(previous_version, version)
            for previous_version, version in zip(chain([None], versions[:-1]), versions)
        ]
