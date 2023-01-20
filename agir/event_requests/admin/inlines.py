from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from agir.event_requests import models
from agir.event_requests.models import EventRequest


class EventThemeInline(admin.TabularInline):
    model = models.EventTheme
    extra = 0
    show_change_link = True
    exclude = ("description",)


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
    fields = ("event_speaker", "date", "available", "accepted", "validate")
    readonly_fields = (
        "accepted",
        "validate",
    )
    ordering = ("-accepted", "-available")

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def validate(self, obj):
        if not obj.available or obj.event_request.status != EventRequest.Status.PENDING:
            return "-"

        return mark_safe(
            '<a class="button" href="%s">Valider</a>'
            % (
                reverse(
                    "admin:event_requests_eventspeakerrequest_validate",
                    args=(obj.pk,),
                )
            )
        )

    validate.short_description = "Validation"
