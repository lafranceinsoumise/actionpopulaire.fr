from django import forms
from django.contrib import admin
from django.urls import reverse, path
from django.utils.safestring import mark_safe
from rangefilter.filters import DateRangeFilter

from agir.event_requests import models
from agir.event_requests.admin import inlines, views, filter as filters
from agir.lib.admin.panels import PersonLinkMixin
from agir.lib.form_fields import MultiDateTimeField


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

    class Media:
        pass


class EventRequestAdminForm(forms.ModelForm):
    datetimes = MultiDateTimeField()

    class Meta:
        model = models.EventRequest
        fields = "__all__"


@admin.register(models.EventRequest)
class EventRequestAdmin(admin.ModelAdmin):
    form = EventRequestAdminForm
    readonly_fields = ("event",)
    list_display = (
        "__str__",
        "created",
        "date_list",
        "status",
        "answered_count",
        "event_link",
    )
    list_filter = (
        "status",
        "event_theme__event_theme_type",
        filters.EventThemesAutocompleteFilter,
        filters.EventAutocompleteFilter,
    )
    inlines = (inlines.EventSpeakerRequestInline,)
    date_hierarchy = "created"

    def answered_count(self, obj):
        if obj.status != self.model.Status.PENDING:
            return "-"

        count = (
            obj.event_speaker_requests.answered()
            .distinct("event_speaker_id")
            .order_by("event_speaker_id")
            .count()
        )

        if count == 0:
            return "-"

        return count

    answered_count.short_description = "Réponses"

    def date_list(self, obj):
        return ", ".join(obj.simple_datetimes)

    date_list.short_description = "Dates possibles"

    def event_link(self, obj):
        if obj.event is None:
            return "-"

        return mark_safe(
            '<a href="%s">%s</a>'
            % (
                reverse(
                    "admin:events_event_change",
                    args=(obj.event.id,),
                ),
                obj.event.name,
            )
        )

    event_link.short_description = "Événement"

    class Media:
        pass


@admin.register(models.EventSpeakerRequest)
class EventSpeakerRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "event_request_link",
        "event_speaker_link",
        "datetime",
        "available",
        "accepted",
        "created",
        "modified",
        "validate",
    )
    list_filter = (
        "available",
        "accepted",
        "event_request__status",
        filters.EventSpeakerAutocompleteFilter,
        ("datetime", DateRangeFilter),
    )
    createonly_fields = (
        "event_request",
        "event_speaker",
        "datetime",
    )
    readonly_fields = (
        "accepted",
        "validate",
    )
    date_hierarchy = "datetime"

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

    event_request_link.short_description = "Demande"

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

    event_speaker_link.short_description = "Intervenant·e"

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

    class Media:
        pass
