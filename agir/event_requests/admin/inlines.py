from django.contrib import admin

from agir.event_requests import models


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
    fields = ("event_speaker", "event_request_date", "available")

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False
