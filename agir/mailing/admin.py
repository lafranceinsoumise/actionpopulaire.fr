from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin

from agir.api.admin import admin_site
from agir.lib.admin import CenterOnFranceMixin
from agir.mailing.models import Segment


@admin.register(Segment, site=admin_site)
class SegmentAdmin(CenterOnFranceMixin, OSMGeoAdmin):
    autocomplete_fields = ("tags", "supportgroup_subtypes")
    readonly_fields = ("get_subscribers_count",)
