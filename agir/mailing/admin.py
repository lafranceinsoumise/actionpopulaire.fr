from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.gis.admin import OSMGeoAdmin
from django.forms import ModelForm

from agir.lib.admin import CenterOnFranceMixin
from agir.mailing.models import Segment


class SegmentAdminForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["countries"].widget = FilteredSelectMultiple(
            "pays", False, choices=self.fields["countries"].choices
        )
        self.fields["departements"].widget = FilteredSelectMultiple(
            "départements", False, choices=self.fields["departements"].choices
        )


@admin.register(Segment)
class SegmentAdmin(CenterOnFranceMixin, OSMGeoAdmin):
    form = SegmentAdminForm
    save_as = True
    fieldsets = (
        (None, {"fields": ("name", "tags", "exclude_segments", "force_non_insoumis")}),
        (
            "GA, événements et formulaires",
            {
                "fields": (
                    "supportgroup_status",
                    "supportgroup_subtypes",
                    "events",
                    "events_start_date",
                    "events_end_date",
                    "events_organizer",
                    "forms",
                    "polls",
                )
            },
        ),
        ("Géographie", {"fields": ("countries", "departements", "area")}),
        (
            "Historique d'utilisation",
            {
                "fields": (
                    "campaigns",
                    "campaigns_feedback",
                    "registration_date",
                    "last_login",
                )
            },
        ),
        (
            "Informations personelles",
            {"fields": ("gender", "born_after", "born_before")},
        ),
        (
            "Historique des dons",
            {
                "fields": (
                    "donation_after",
                    "donation_not_after",
                    "donation_total_min",
                    "donation_total_max",
                    "donation_total_range",
                    "subscription",
                )
            },
        ),
        ("Combiner des segments", {"fields": ("add_segments",)}),
        ("Abonnés", {"fields": ("get_subscribers_count",)}),
    )
    map_template = "custom_fields/french_area_widget.html"
    autocomplete_fields = (
        "tags",
        "supportgroup_subtypes",
        "events",
        "events_subtypes",
        "campaigns",
        "exclude_segments",
        "add_segments",
        "forms",
        "polls",
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
