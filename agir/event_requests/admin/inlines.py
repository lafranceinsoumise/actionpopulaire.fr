from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from agir.event_requests import models
from agir.event_requests.models import EventRequest
from agir.lib.admin.inlines import NonrelatedTabularInline


class EventAssetTemplateInline(NonrelatedTabularInline):
    verbose_name = "Template de visuel"
    verbose_name_plural = "Templates de visuels"
    model = models.EventAssetTemplate
    fields = ("name", "file")
    extra = 0

    def get_form_queryset(self, obj):
        return obj.event_asset_templates.all()

    def save_new_instance(self, parent, instance):
        instance.save()
        parent.event_asset_templates.add(instance)


class EventThemeInline(admin.TabularInline):
    model = models.EventTheme
    extra = 0
    show_change_link = True
    exclude = ("description", "event_asset_templates")


class EventSpeakerThemeInline(admin.TabularInline):
    model = models.EventSpeaker.event_themes.through
    extra = 0
    can_delete = False
    show_change_link = True
    verbose_name = "thème"
    verbose_name_plural = "thèmes"

    def has_change_permission(self, request, obj=None):
        return False


class EventThemeSpeakerInline(admin.TabularInline):
    model = models.EventSpeaker.event_themes.through
    extra = 0
    can_delete = False
    show_change_link = True
    verbose_name = "intervenant·e"
    verbose_name_plural = "intervenant·es"
    autocomplete_fields = ("eventspeaker",)

    def has_change_permission(self, request, obj=None):
        return False


class EventSpeakerRequestInline(admin.TabularInline):
    model = models.EventSpeakerRequest
    extra = 0
    can_delete = False
    show_change_link = True
    verbose_name = "demandes de disponibilité"
    verbose_name_plural = "demandes de disponibilité"
    fields = (
        "event_speaker",
        "datetime",
        "available",
        "comment",
        "accepted",
        "validate",
    )
    readonly_fields = (
        "accepted",
        "validate",
    )
    ordering = ("-accepted", "-available")

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(description="Validation", empty_value="-")
    def validate(self, obj):
        if not obj.available or obj.event_request.status != EventRequest.Status.PENDING:
            return

        return mark_safe(
            '<a class="button" href="%s">Valider</a>'
            % (
                reverse(
                    "admin:event_requests_eventspeakerrequest_validate",
                    args=(obj.pk,),
                )
            )
        )
