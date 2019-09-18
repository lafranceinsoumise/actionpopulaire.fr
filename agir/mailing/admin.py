from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin

from agir.api.admin import admin_site
from agir.lib.admin import CenterOnFranceMixin
from agir.mailing.models import Segment


@admin.register(Segment, site=admin_site)
class SegmentAdmin(CenterOnFranceMixin, OSMGeoAdmin):
    autocomplete_fields = ("tags", "supportgroup_subtypes")
    readonly_fields = ("get_subscribers_count",)
    ordering = ("name",)
    search_fields = ("name",)
    list_filter = ("supportgroup_status", "supportgroup_subtypes", "tags")
    list_display = (
        "name",
        "supportgroup_status",
        "supportgroup_subtypes_list",
        "tags_list",
    )

    def supportgroup_subtypes_list(self, instance):
        return ", ".join(str(s) for s in instance.supportgroup_subtypes.all())

    def tags_list(self, instance):
        return ", ".join(str(t) for t in instance.tags.all())
