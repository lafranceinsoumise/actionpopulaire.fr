from itertools import chain

from django.urls import reverse
from django.utils.html import format_html
from reversion.models import Version


class HistoryMixin:
    DIFFED_FIELDS = []

    @classmethod
    def get_history_step(cls, old, new, **kwargs):
        old_fields = old.field_dict if old else {}
        new_fields = new.field_dict
        revision = new.revision
        person = revision.user.person if revision.user else None

        res = {
            "modified": revision.date_created,
            "comment": revision.get_comment(),
            "diff": cls.get_diff(old_fields, new_fields) if old_fields else [],
        }

        if person:
            res["user"] = format_html(
                '<a href="{url}">{text}</a>',
                url=reverse("admin:people_person_change", args=[person.pk]),
                text=person.get_short_name(),
            )
        else:
            res["user"] = "Utilisateur inconnu"

        if old is None:
            res["title"] = "Création"
        else:
            res["title"] = "Modification"

        return res

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
