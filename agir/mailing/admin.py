from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin

from agir.api.admin import admin_site
from agir.lib.admin import CenterOnFranceMixin
from agir.mailing.models import Segment


@admin.register(Segment, site=admin_site)
class SegmentAdmin(CenterOnFranceMixin, OSMGeoAdmin):
    fieldsets = (
        (None, {"fields": ("name", "tags", "exclude_segments")}),
        (
            "GA et événements",
            {
                "fields": (
                    "supportgroup_status",
                    "supportgroup_subtypes",
                    "events",
                    "events_start_date",
                    "events_end_date",
                    "events_organizer",
                )
            },
        ),
        ("Géographie", {"fields": ("area",)}),
        (
            "Historique d'utilisation",
            {"fields": ("campaigns", "registration_date", "last_login")},
        ),
        (
            "Informations personelles",
            {"fields": ("gender", "born_after", "born_before")},
        ),
        ("Historique des dons", {"fields": ("donation_after", "subscription")}),
    )
    map_template = "custom_fields/french_area_widget.html"
    autocomplete_fields = (
        "tags",
        "supportgroup_subtypes",
        "events",
        "events_subtypes",
        "campaigns",
        "exclude_segments",
    )
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
