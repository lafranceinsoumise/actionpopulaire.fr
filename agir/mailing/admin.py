from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.gis.admin import OSMGeoAdmin
from django.db.models import Q
from django.forms import ModelForm, CheckboxSelectMultiple
from django.template.response import TemplateResponse
from django.urls import reverse
from nuntius.admin import (
    CampaignAdmin,
    CampaignSentEventAdmin,
    PushCampaignAdmin,
    PushCampaignSentEventAdmin,
)
from nuntius.models import (
    Campaign,
    CampaignSentEvent,
    PushCampaign,
    PushCampaignSentEvent,
)

from agir.lib.admin.panels import CenterOnFranceMixin
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

    class Meta:
        widgets = {
            "newsletters": CheckboxSelectMultiple,
        }


@admin.register(Segment)
class SegmentAdmin(CenterOnFranceMixin, OSMGeoAdmin):
    form = SegmentAdminForm
    save_as = True
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "newsletters",
                    "tags",
                    "is_2022",
                    "is_insoumise",
                )
            },
        ),
        (
            "GA, événements, tirage au sort et formulaires",
            {
                "fields": (
                    "draw_status",
                    "supportgroup_status",
                    "supportgroup_subtypes",
                    "events",
                    "events_start_date",
                    "events_end_date",
                    "events_subtypes",
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
                    "last_open",
                    "last_click",
                    "registration_date",
                    "registration_date_before",
                    "last_login",
                    "registration_duration",
                )
            },
        ),
        (
            "Informations personnelles",
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
        (
            "Réseau des élus",
            {
                "fields": (
                    "elu",
                    "elu_municipal",
                    "elu_departemental",
                    "elu_regional",
                    "elu_consulaire",
                    "elu_depute",
                    "elu_depute_europeen",
                )
            },
        ),
        ("Combiner des segments", {"fields": ("add_segments", "exclude_segments")}),
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


@admin.register(Campaign)
class NuntiusCampaignAdmin(CampaignAdmin):
    list_display = (
        "name",
        "message_subject",
        "segment",
        "status",
        "send_button",
    )

    def send_view(self, request, pk):
        if request.POST.get("confirmation"):
            return super().send_view(request, pk)

        campaign = Campaign.objects.get(pk=pk)
        # Ask for the user to confirm before actually sending the campaign
        # if the campaign's segment contains one or more subscribers
        # with no newsletter subscription
        should_confirm = (
            campaign.segment.get_subscribers_queryset()
            .filter(newsletters__len=0)
            .exists()
        )

        if not should_confirm:
            return super().send_view(request, pk)

        request.current_app = self.admin_site.name
        context = {
            "pk": pk,
            "edit_campaign_link": reverse("admin:nuntius_campaign_change", args=[pk]),
        }
        return TemplateResponse(
            request, "admin/send_campaign_action_confirmation.html", context
        )


@admin.register(PushCampaign)
class NuntiusPushCampaignAdmin(PushCampaignAdmin):
    def segment_subscribers(self, instance):
        if not instance.segment:
            return "-"
        return (
            instance.segment.get_subscribers_queryset()
            .filter(Q(role__gcmdevice__active=True) | Q(role__apnsdevice__active=True))
            .count()
        )


admin.site.register(CampaignSentEvent, CampaignSentEventAdmin)
admin.site.register(PushCampaignSentEvent, PushCampaignSentEventAdmin)
