from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import reverse, path
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from rangefilter.filters import DateRangeFilter

from agir.event_requests import models
from agir.event_requests.admin import inlines, views, filter as filters
from agir.event_requests.admin.forms import EventRequestAdminForm
from agir.lib.admin.panels import PersonLinkMixin
from agir.lib.utils import front_url


@admin.register(models.EventAssetTemplate)
class EventAssetTemplateAdmin(admin.ModelAdmin):
    search_fields = ("name", "file")
    readonly_fields = ("template_preview",)

    @admin.display(description="Aperçu du template", empty_value="-")
    def template_preview(self, obj):
        if not obj or not obj.file:
            return

        return format_html(
            f"<img width='400' height='400' "
            f"style='clear:right; display: block; width:auto; height: auto; max-width: 400px; max-height: 400px;' "
            f"src={obj.file.url} />"
        )

    def get_model_perms(self, request):
        return {}


@admin.register(models.EventAsset)
class EventAssetAdmin(admin.ModelAdmin):
    list_display = ("name", "event_link", "file", "deprecated")
    search_fields = ("name", "event__search")
    readonly_fields = ("event_link", "file", "deprecated", "template_preview", "render")
    autocomplete_fields = ("template",)

    @admin.display(description="Visuel obsolète", boolean=True)
    def deprecated(self, obj):
        return obj and obj.deprecated

    @admin.display(description="Événement", empty_value="-")
    def event_link(self, obj):
        if obj.event:
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

    @admin.display(description="Aperçu du template", empty_value="-")
    def template_preview(self, obj):
        if not obj or obj.deprecated:
            return

        return format_html(
            f"<img width='400' height='400' "
            f"style='clear:right; display: block; width:auto; height: auto; max-width: 400px; max-height: 400px;' "
            f"src={obj.template.file.url} />"
        )

    @admin.display(description="Actions", empty_value="-")
    def render(self, obj):
        if not obj or obj.deprecated:
            return

        return format_html(
            "<form>"
            "<input type='submit' name='_render' value='Régénérer le visuel' />"
            "</form>"
            "<div class='help' style='margin: .5rem 0 0; padding: 0;'>"
            "<strong>⚠ Attention&nbsp;:</strong> le visuel existant sera définitivement supprimé"
            "</div>"
        )

    def response_change(self, request, obj):
        if "_render" in request.POST:
            try:
                obj.render()
                self.message_user(
                    request, "Un nouveau visuel a été régénéré à partir du template."
                )
            except Exception as e:
                self.message_user(
                    request,
                    str(e),
                    level=messages.WARNING,
                )
            return HttpResponseRedirect(".")
        return super().response_change(request, obj)

    class Media:
        pass


@admin.register(models.EventThemeType)
class EventThemeTypeAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            None,
            {"fields": ("name", "event_subtype", "calendar_link")},
        ),
        (
            "DEMANDES DE DISPONIBILITÉ",
            {
                "fields": (
                    "event_speaker_request_email_from",
                    "event_speaker_request_email_subject",
                    "event_speaker_request_email_body",
                )
            },
        ),
    )
    list_display = ("name", "event_subtype", "calendar_link")
    list_filter = ("event_theme",)
    search_fields = ("name",)
    autocomplete_fields = ("event_subtype",)
    readonly_fields = ("calendar_link",)
    inlines = (inlines.EventThemeInline, inlines.EventAssetTemplateInline)
    exclude = ("event_asset_templates",)

    @admin.display(description="Agenda", empty_value="-")
    def calendar_link(self, obj):
        if obj.calendar:
            return format_html(
                '<a href="{0}">{0}</a>',
                front_url(
                    "view_calendar", kwargs={"slug": obj.calendar.slug}, absolute=True
                ),
            )


@admin.register(models.EventTheme)
class EventThemeAdmin(admin.ModelAdmin):
    list_display = ("name", "event_theme_type", "calendar_link")
    list_filter = ("event_theme_type",)
    search_fields = ("name", "event_theme_type__name")
    autocomplete_fields = ("event_theme_type",)
    readonly_fields = ("calendar_link",)
    inlines = (
        inlines.EventThemeSpeakerInline,
        inlines.EventAssetTemplateInline,
    )
    exclude = ("event_asset_templates",)

    @admin.display(description="Agenda", empty_value="-")
    def calendar_link(self, obj):
        if obj.calendar:
            return format_html(
                '<a href="{0}">{0}</a>',
                front_url(
                    "view_calendar", kwargs={"slug": obj.calendar.slug}, absolute=True
                ),
            )


@admin.register(models.EventSpeaker)
class EventSpeakerAdmin(admin.ModelAdmin, PersonLinkMixin):
    list_filter = ("available", "event_themes")
    list_display = ("id", "person_link", "themes", "available")
    inlines = (inlines.EventSpeakerThemeInline, inlines.EventSpeakerRequestInline)
    search_fields = ("person__search",)
    exclude = ("event_themes",)
    autocomplete_fields = ("person",)

    @admin.display(description="Thèmes", empty_value="-")
    def themes(self, obj):
        return ", ".join(obj.event_themes.values_list("name", flat=True))

    class Media:
        pass


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

    @admin.display(description="Réponses", empty_value="-")
    def answered_count(self, obj):
        if obj.status != self.model.Status.PENDING:
            return

        count = (
            obj.event_speaker_requests.answered()
            .distinct("event_speaker_id")
            .order_by("event_speaker_id")
            .count()
        )

        if count == 0:
            return

        return count

    @admin.display(description="Dates", empty_value="-")
    def date_list(self, obj):
        return ", ".join(obj.simple_datetimes)

    @admin.display(description="Événement", empty_value="-")
    def event_link(self, obj):
        if obj.event:
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

    @admin.display(description="Demande", empty_value="-")
    def event_request_link(self, obj):
        if obj.event_request:
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

    @admin.display(description="Intervenant·e", empty_value="-")
    def event_speaker_link(self, obj):
        if obj.event_speaker:
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

    @admin.display(description="Validation", empty_value="-")
    def validate(self, obj):
        if (
            not obj.available
            or obj.event_request.status != obj.event_request.Status.PENDING
        ):
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

    class Media:
        pass
