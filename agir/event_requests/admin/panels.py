from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import reverse, path
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import ngettext
from rangefilter.filters import DateRangeFilter

from agir.event_requests import models, actions
from agir.event_requests.admin import inlines, views, filter as filters
from agir.event_requests.admin.forms import EventRequestAdminForm
from agir.lib.admin.panels import PersonLinkMixin
from agir.lib.admin.utils import admin_url, display_list_of_links
from agir.lib.utils import front_url


@admin.register(models.EventAssetTemplate)
class EventAssetTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "file", "target_format")
    list_filter = ("target_format",)
    search_fields = ("name", "file")
    readonly_fields = ("template_preview",)

    @admin.display(description="Aperçu du template")
    def template_preview(self, obj):
        if not obj or not obj.file:
            return "-"

        return format_html(
            f"<img width='400' height='400' "
            f"style='clear:right; display: block; width:auto; height: auto; max-width: 400px; max-height: 400px;' "
            f"src={obj.file.url} />"
        )


@admin.register(models.EventAsset)
class EventAssetAdmin(admin.ModelAdmin):
    list_display = ("name", "event_link", "file", "published")
    list_filter = (
        "published",
        filters.EventAutocompleteFilter,
    )
    search_fields = ("name", "event__name")
    readonly_fields = ("event_link", "published", "render")
    create_only_fields = ("event",)
    exclude = ("renderable",)
    autocomplete_fields = ("template", "event")

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj)
        if obj is None:
            return fields + self.create_only_fields
        return fields

    @admin.display(description="Événement")
    def event_link(self, obj):
        if not obj.event:
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

    @admin.display(description="Actions")
    def render(self, obj):
        actions = []

        if obj and not obj.published:
            actions.append(
                mark_safe(
                    "<input type='submit' name='_publish' value='Publier le visuel' />"
                    "<p class='help' style='margin: 0; padding: 0.25rem 0;'>"
                    "Les organisateur·ices recevront une notification et pourront accèder au visuel "
                    "dans le volet de gestion de la page de l'événement"
                    "</p>"
                )
            )

        if obj and obj.published:
            actions.append(
                mark_safe(
                    "<input type='submit' name='_unpublish' value='Dépublier le visuel' />"
                )
            )

        if obj and obj.renderable:
            actions.append(
                mark_safe(
                    "<input type='submit' name='_render' value='Régénérer le visuel' />"
                    "<p class='help' style='margin: 0; padding: 0.25rem 0;'>"
                    "<strong>⚠ Attention&nbsp;:</strong> le visuel existant sera définitivement supprimé"
                    "</p>"
                )
            )

        if actions:
            return format_html(
                "<form style='margin: .5rem 0; padding: 0;'>{}</form>",
                mark_safe("<br />".join(actions)),
            )

        return "-"

    @admin.display(description="Publier les visuels sélectionnés")
    def publish(self, _modeladmin, request, queryset):
        if isinstance(queryset, self.model):
            queryset = self.model.objects.filter(pk=queryset.pk)
        updated_count = actions.publish_event_assets(queryset)
        self.message_user(
            request,
            ngettext(
                "Le visuel a été publié.",
                f"{updated_count} visuels ont été publiés",
                updated_count,
            ),
        )

    @admin.display(description="Dépublier les visuels sélectionnés")
    def unpublish(self, _modeladmin, request, queryset):
        if isinstance(queryset, self.model):
            queryset = self.model.objects.filter(pk=queryset.pk)
        updated_count = actions.unpublish_event_assets(queryset)
        self.message_user(
            request,
            ngettext(
                "Le visuel a été dépublié.",
                f"{updated_count} visuels ont été dépubliés",
                updated_count,
            ),
        )

    def get_actions(self, request):
        self.actions = (self.publish, self.unpublish)
        return super().get_actions(request)

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

        if "_publish" in request.POST:
            try:
                self.publish(self, request, obj)
            except Exception as e:
                self.message_user(
                    request,
                    str(e),
                    level=messages.WARNING,
                )
            return HttpResponseRedirect(".")

        if "_unpublish" in request.POST:
            try:
                self.unpublish(self, request, obj)
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
            {"fields": ("name", "event_subtype", "calendar_link", "map_link")},
        ),
        (
            "ADRESSES E-MAIL",
            {
                "fields": (
                    "email_from",
                    "email_to",
                )
            },
        ),
        (
            "EMAIL DE DEMANDE DE DISPONIBILITÉ",
            {
                "fields": (
                    "has_event_speaker_request_emails",
                    "event_speaker_request_email_subject",
                    "event_speaker_request_email_body",
                )
            },
        ),
        (
            "TEMPLATES DE VISUELS",
            {"fields": ("event_asset_templates",)},
        ),
    )
    list_display = ("name", "event_subtype", "calendar_link", "map_link")
    list_filter = ("event_theme",)
    search_fields = ("name",)
    autocomplete_fields = ("event_subtype",)
    filter_horizontal = ("event_asset_templates",)
    readonly_fields = (
        "calendar_link",
        "map_link",
    )
    inlines = (
        inlines.EventAssetTemplateInline,
        inlines.EventThemeInline,
    )

    @admin.display(description="Agenda")
    def calendar_link(self, obj):
        if not obj or not obj.calendar:
            return "-"
        return format_html(
            '<a href="{0}">{0}</a>',
            front_url(
                "view_calendar", kwargs={"slug": obj.calendar.slug}, absolute=True
            ),
        )

    @admin.display(description="Carte")
    def map_link(self, obj):
        if not obj:
            return "-"
        return format_html(
            '<a href="{0}">Carte des événements à venir</a>',
            front_url(
                "carte:events_map",
                absolute=True,
                query={"subtype": obj.event_subtype.label},
            ),
        )


@admin.register(models.EventTheme)
class EventThemeAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "description",
                    "event_theme_type",
                    "calendar_link",
                )
            },
        ),
        (
            "NOTIFICATION DE CRÉATION D'ÉVÉNEMENT À L'INTERVENANT·E",
            {
                "fields": (
                    "speaker_event_creation_email_subject",
                    "speaker_event_creation_email_body",
                )
            },
        ),
        (
            "NOTIFICATION DE CRÉATION D'ÉVÉNEMENT À L'ORGANISATEUR·ICE",
            {
                "fields": (
                    "organizer_event_creation_email_subject",
                    "organizer_event_creation_email_body",
                )
            },
        ),
        (
            "NOTIFICATION DE CRÉATION D'ÉVÉNEMENT À L'ADMINISTRATEUR·ICE",
            {
                "fields": (
                    "email_to",
                    "event_creation_notification_email_subject",
                    "event_creation_notification_email_body",
                )
            },
        ),
        (
            "NOTIFICATION DE CRÉATION D'ÉVÉNEMENT AUX INTERVENANT·ES NON RETENU·ES",
            {
                "fields": (
                    "unretained_speaker_event_creation_email_subject",
                    "unretained_speaker_event_creation_email_body",
                )
            },
        ),
        (
            "TEMPLATES DE VISUELS",
            {"fields": ("event_asset_templates",)},
        ),
    )
    list_display = (
        "name",
        "event_theme_type_link",
        "calendar_link",
        "speaker_email",
        "organizer_email",
        "notification_email",
        "unretained_speaker_email",
        "event_speaker_count",
    )
    list_filter = ("event_theme_type",)
    search_fields = ("name", "event_theme_type__name")
    autocomplete_fields = ("event_theme_type",)
    readonly_fields = ("calendar_link", "email_to")
    filter_horizontal = ("event_asset_templates",)
    inlines = (
        inlines.EventAssetTemplateInline,
        inlines.EventThemeSpeakerInline,
    )

    def get_queryset(self, request):
        return super().get_queryset(request).with_admin_prefetch()

    @admin.display(description="Destinataire")
    def email_to(self, obj):
        return obj.event_theme_type.email_to

    @admin.display(description="Agenda")
    def calendar_link(self, obj):
        if not obj or not obj.calendar:
            return "-"
        return format_html(
            '<a href="{0}">{0}</a>',
            front_url(
                "view_calendar", kwargs={"slug": obj.calendar.slug}, absolute=True
            ),
        )

    @admin.display(description="Type")
    def event_theme_type_link(self, obj):
        if not obj:
            return "-"
        return format_html(
            '<a href="{}">{}</a>',
            admin_url(
                "admin:event_requests_eventthemetype_change",
                args=(obj.event_theme_type_id,),
                absolute=True,
            ),
            str(obj.event_theme_type),
        )

    @admin.display(description="@ intervenant·e", boolean=True)
    def speaker_email(self, obj):
        return obj.get_speaker_event_creation_email_bindings() is not None

    @admin.display(description="@ organisateur·ice", boolean=True)
    def organizer_email(self, obj):
        return obj.get_organizer_event_creation_email_bindings() is not None

    @admin.display(description="@ administrateur·ice", boolean=True)
    def notification_email(self, obj):
        return obj.get_event_creation_notification_email_bindings() is not None

    @admin.display(description="@ non retenu·es", boolean=True)
    def unretained_speaker_email(self, obj):
        return obj.get_unretained_speaker_event_creation_email_bindings() is not None

    @admin.display(description="Nb d'intervenant·es", ordering="event_speaker_count")
    def event_speaker_count(self, obj):
        if hasattr(obj, "event_speaker_count"):
            return obj.event_speaker_count
        return "-"


@admin.register(models.EventSpeaker)
class EventSpeakerAdmin(admin.ModelAdmin, PersonLinkMixin):
    list_display = ("id", "person_link", "description", "themes", "available")
    list_filter = (
        "available",
        "event_themes",
        "event_themes__event_theme_type",
    )
    inlines = (
        inlines.EventSpeakerUpcomingEventInline,
        inlines.EventSpeakerPastEventInline,
    )
    search_fields = (
        "description",
        "person__search",
    )
    autocomplete_fields = ("person", "event_themes")

    def get_queryset(self, request):
        return super().get_queryset(request).with_admin_prefetch()

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
        "event_speaker_link",
    )
    list_filter = (
        "status",
        "event_theme__event_theme_type",
        filters.EventThemesAutocompleteFilter,
        filters.EventAutocompleteFilter,
    )
    inlines = (inlines.EventSpeakerRequestInline,)
    date_hierarchy = "created"

    @admin.display(description="Réponses")
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

    @admin.display(description="Dates")
    def date_list(self, obj):
        return ", ".join(obj.simple_datetimes)

    @admin.display(description="Événement")
    def event_link(self, obj):
        if not obj or not obj.event:
            return "-"
        return mark_safe(
            '<a href="%s">%s</a>'
            % (
                reverse(
                    "admin:events_event_change",
                    args=(obj.event_id,),
                ),
                obj.event.name,
            )
        )

    @admin.display(description="Intervenant·es")
    def event_speaker_link(self, obj):
        if not obj or not obj.event:
            return "-"

        event_speakers = list(obj.event.event_speakers.all())
        if not event_speakers:
            return "-"

        return display_list_of_links(
            [(event_speaker, str(event_speaker)) for event_speaker in event_speakers]
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

    @admin.display(description="Demande")
    def event_request_link(self, obj):
        if not obj or not obj.event_request:
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

    @admin.display(description="Intervenant·e")
    def event_speaker_link(self, obj):
        if not obj.event_speaker:
            return "-"

        return mark_safe(
            '<a href="%s">%s</a>'
            % (
                reverse(
                    "admin:event_requests_eventspeaker_change",
                    args=(obj.event_speaker_id,),
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

    @admin.display(description="Validation")
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

    class Media:
        pass
