from django.contrib import admin
from django.urls import reverse, path
from django.utils.safestring import mark_safe
from rangefilter.filters import DateRangeFilter

from agir.event_requests import models
from agir.event_requests.admin import inlines, views
from agir.lib.admin.panels import PersonLinkMixin


@admin.register(models.EventRequestDate)
class EventRequestDateAdmin(admin.ModelAdmin):
    createonly_fields = ("date",)
    search_fields = ("date",)

    def has_module_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj is None:
            return readonly_fields
        return readonly_fields + self.createonly_fields


@admin.register(models.EventThemeType)
class EventThemeTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "event_subtype")
    list_filter = ("event_theme",)
    autocomplete_fields = ("event_subtype",)
    inlines = (inlines.EventThemeInline,)
    search_fields = ("name",)


@admin.register(models.EventTheme)
class EventThemeAdmin(admin.ModelAdmin):
    list_filter = ("event_theme_type",)
    list_display = ("name", "event_theme_type")
    inlines = (inlines.EventThemeSpeakerInline,)
    autocomplete_fields = ("event_theme_type",)


@admin.register(models.EventSpeaker)
class EventSpeakerAdmin(admin.ModelAdmin, PersonLinkMixin):
    list_filter = ("available", "event_themes")
    list_display = ("id", "person_link", "themes", "available")
    inlines = (inlines.EventSpeakerThemeInline, inlines.EventSpeakerRequestInline)
    search_fields = ("person__search",)
    exclude = ("event_themes",)

    def themes(self, obj):
        return ", ".join(obj.event_themes.values_list("name", flat=True))

    themes.short_description = "Thèmes"


@admin.register(models.EventRequest)
class EventRequestAdmin(admin.ModelAdmin):
    readonly_fields = ("event",)
    list_display = ("__str__", "date_list", "status", "event")
    inlines = (inlines.EventSpeakerRequestInline,)
    autocomplete_fields = ("dates",)

    def date_list(self, obj):
        return obj.date_list

    date_list.short_description = "Dates possibles"


@admin.register(models.EventSpeakerRequest)
class EventSpeakerRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "event_request_link",
        "event_speaker_link",
        "event_request_date",
        "available",
        "created",
        "modified",
        "validate",
    )
    list_filter = (
        "available",
        "event_request__status",
        "event_speaker",
        ("event_request_date__date", DateRangeFilter),
    )
    createonly_fields = (
        "event_request",
        "event_speaker",
        "event_request_date",
    )
    readonly_fields = ("validate",)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj is None:
            return readonly_fields
        return readonly_fields + self.createonly_fields

    def event_request_link(self, obj):
        if obj.event_request is None:
            return "-"

        return mark_safe(
            '<a href="%s">%s</a>'
            % (
                reverse(
                    "admin:event_requests_eventrequest_change",
                    args=(obj.event_request.id,),
                ),
                obj.event_request,
            )
        )

    event_request_link.short_description = "demande"

    def event_speaker_link(self, obj):
        if obj.event_speaker is None:
            return "-"

        return mark_safe(
            '<a href="%s">%s</a>'
            % (
                reverse(
                    "admin:event_requests_eventspeaker_change",
                    args=(obj.event_speaker.id,),
                ),
                obj.event_speaker,
            )
        )

    event_speaker_link.short_description = "intervenant·e"

    def get_urls(self):
        return [
            path(
                "<uuid:pk>/validate/",
                self.admin_site.admin_view(self.validate_event_speaker_request),
                name="{}_{}_validate".format(self.opts.app_label, self.opts.model_name),
            )
        ] + super().get_urls()

    def validate_event_speaker_request(self, request, pk):
        return views.validate_event_speaker_request(self, request, pk)

    def validate(self, obj):
        if (
            not obj.available
            or obj.event_request.status != obj.event_request.Status.PENDING
        ):
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
