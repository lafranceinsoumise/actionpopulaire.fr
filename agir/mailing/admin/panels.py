from copy import deepcopy

from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.html import format_html
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
from agir.lib.admin.utils import admin_url
from agir.mailing.admin import list_filters, actions
from agir.mailing.admin.forms import SegmentAdminForm
from agir.mailing.models import Segment


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
                    "excluded_tags",
                    "is_political_support",
                    "is_2022",
                    "is_insoumise",
                )
            },
        ),
        (
            "Statut",
            {
                "fields": (
                    "qualifications",
                    "person_qualification_status",
                )
            },
        ),
        (
            "Groupes d'action",
            {
                "fields": (
                    "supportgroup_status",
                    "supportgroup_is_certified",
                    "supportgroup_types",
                    "supportgroup_subtypes",
                    "supportgroups",
                )
            },
        ),
        (
            "Événements",
            {
                "fields": (
                    "events",
                    "excluded_events",
                    "events_start_date",
                    "events_end_date",
                    "events_subtypes",
                    "events_organizer",
                )
            },
        ),
        (
            "Tirage au sort et formulaires",
            {
                "fields": (
                    "draw_status",
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
                    "elu_status",
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
        (
            "Personnes",
            {
                "fields": (
                    "subscribers_count",
                    "people_count",
                )
            },
        ),
        (
            "Export",
            {
                "permission": "segment.export_segment",
                "fields": ("download_for_sms_link",),
            },
        ),
    )
    map_template = "custom_fields/french_area_widget.html"
    autocomplete_fields = (
        "tags",
        "excluded_tags",
        "qualifications",
        "supportgroups",
        "supportgroup_subtypes",
        "events",
        "excluded_events",
        "events_subtypes",
        "campaigns",
        "exclude_segments",
        "add_segments",
        "forms",
        "polls",
    )
    readonly_fields = ("people_count", "subscribers_count", "download_for_sms_link")
    ordering = ("name",)
    search_fields = ("name",)
    list_filter = (
        "supportgroup_status",
        list_filters.SupportGroupSubtypeListFilter,
        list_filters.TagListFilter,
        list_filters.ExcludedTagListFilter,
        list_filters.QualificationListFilter,
        ("elu", admin.EmptyFieldListFilter),
    )
    list_display = (
        "name",
        "supportgroup_status",
        "supportgroup_subtypes_list",
        "tags_list",
        "subscriber_list_link",
        "has_elu",
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = deepcopy(super().get_fieldsets(request, obj))
        authorized_fieldsets = []
        for key, props in fieldsets:
            permission = props.pop("permission", False)
            if not permission or request.user.has_perm(permission):
                authorized_fieldsets.append((key, props))
        return tuple(authorized_fieldsets)

    @admin.display(description="Types de groupe")
    def supportgroup_subtypes_list(self, instance):
        return ", ".join(str(s) for s in instance.supportgroup_subtypes.all())

    @admin.display(description="Tags")
    def tags_list(self, instance):
        tags = [str(t) for t in instance.tags.all()] + [
            f"<span style='text-decoration: line-through rgba(0,0,0,0.5);'>&ensp;{t}&ensp;</span>"
            for t in instance.excluded_tags.all()
        ]
        if not tags:
            return "—"

        return format_html(", ".join(tags))

    @admin.display(description="Nombre de personnes dans le segment")
    def people_count(self, instance):
        if not instance:
            return "-"

        count = instance.get_count()

        if count == 0:
            return "Ce segment est vide"

        return format_html(
            '{} personne{}&ensp;(<a href="{}?segment={}">Voir la liste</a>)',
            count,
            "s" if count > 1 else "",
            reverse("admin:people_person_changelist"),
            str(instance.pk),
        )

    @admin.display(description="Nombre de personnes avec une adresse email valide")
    def subscribers_count(self, instance):
        if not instance:
            return "-"

        count = instance.get_subscribers_count()

        if count == 0:
            return "Ce segment est vide"

        return format_html(
            '{} personne{}&ensp;(<a href="{}?segment={}&bounced_email=0">Voir la liste</a>)',
            count,
            "s" if count > 1 else "",
            reverse("admin:people_person_changelist"),
            str(instance.pk),
        )

    @admin.display(description="Abonné·es")
    def subscriber_list_link(self, instance):
        if not instance:
            return "-"

        return format_html(
            '<a href="{}?segment={}">Voir la liste des personnes</a>',
            reverse("admin:people_person_changelist"),
            str(instance.pk),
        )

    @admin.display(description="Elu·es", boolean=True)
    def has_elu(self, instance):
        return bool(instance.elu)

    @admin.display(description="SMS")
    def download_for_sms_link(self, instance):
        if not instance:
            return "-"

        return format_html(
            '<a href="{}" class="button">💾&ensp;Télécharger pour l\'envoi de SMS</a>',
            admin_url(
                "admin:mailing_segment_download_for_sms", kwargs={"pk": instance.pk}
            ),
        )

    def download_for_sms(self, request, pk):
        if not request.user.is_superuser:
            raise PermissionDenied()

        segment = get_object_or_404(Segment, id=pk)

        return actions.download_segment_as_csv_for_sms(segment)

    def get_urls(self):
        return [
            path(
                "<int:pk>/export/sms/",
                self.admin_site.admin_view(self.download_for_sms),
                name="mailing_segment_download_for_sms",
            ),
        ] + super().get_urls()

    class Media:
        pass


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
