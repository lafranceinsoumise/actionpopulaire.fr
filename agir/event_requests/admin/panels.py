from django.contrib import admin
from django.urls import reverse, path
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from rangefilter.filters import DateRangeFilter

from agir.event_requests import models
from agir.event_requests.admin import inlines, views, filter as filters
from agir.event_requests.admin.forms import EventRequestAdminForm
from agir.lib.admin.panels import PersonLinkMixin
from agir.lib.admin.utils import display_list_of_links, display_link, admin_url
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
    list_display = ("name", "event_link", "file", "published", "is_image")
    list_filter = (
        "published",
        filters.EventAutocompleteFilter,
    )
    search_fields = ("name", "event__name")
    readonly_fields = (
        "event_link",
        "is_event_image",
        "published",
        "preview_image",
        "rendering",
        "publishing",
    )
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
        return display_link(obj.event)

    @admin.display(description="Image de l'événement", boolean=True)
    def is_image(self, obj):
        return obj.is_event_image

    @admin.display(description="Aperçu")
    def preview_image(self, obj):
        if not obj or not obj.renderable:
            return "-"

        img = (
            "<img width='300' height='300' "
            "style='clear:right;display:block;width:100%;height:auto;max-width:300px;' "
            "src={} />"
        )

        src = admin_url(
            f"admin:{self.opts.app_label}_{self.opts.model_name}_preview",
            args=[obj.pk],
        )

        return format_html(img.format(src)) + format_html(
            "<p class='help' style='margin:0;padding: 0.5rem 0;font-size:0.875rem;'>"
            "<strong>⚠ Attention&nbsp;: cette image n'est qu'un aperçu du visuel</strong><br/>Pour générer ou mettre à "
            "jour le fichier, veuillez cliquer sur le bouton `Régénérer le visuel` ci-dessous."
            "</p>"
        )

    @admin.display(description="Actions")
    def rendering(self, obj):
        if obj and obj.renderable:
            return mark_safe(
                "<input type='submit' name='_render' value='⟳ Régénérer le visuel' />"
                "<p class='help' style='margin:0;padding: 0.5rem 0;font-size:0.875rem;'>"
                "<strong>⚠ Attention&nbsp;:</strong> le visuel existant sera définitivement supprimé"
                "</p>"
            )

        return "-"

    @admin.display(description="Publication")
    def publishing(self, obj):
        if obj and not obj.published:
            return mark_safe(
                "<input type='submit' name='_publish' value='✔ Publier le visuel' />"
                "<p class='help' style='margin:0;padding: 0.5rem 0;font-size:0.875rem;'>"
                "Les organisateur·ices recevront une notification et pourront accèder au visuel "
                "dans le volet de gestion de la page de l'événement"
                "</p>"
            )

        if obj and obj.published:
            return mark_safe(
                "<input type='submit' name='_unpublish' value='✖ Dépublier le visuel' />"
            )

        return "-"

    def set_as_event_image(self, request, pk):
        return views.set_event_asset_as_event_image(self, request, pk)

    def preview(self, request, pk):
        return views.preview_event_asset(self, request, pk)

    def render(self, request, pk):
        return views.render_event_asset(self, request, pk)

    def publish(self, request, pk):
        return views.publish_event_assets(self, request, pk)

    def unpublish(self, request, pk):
        return views.unpublish_event_assets(self, request, pk)

    @admin.display(description="Publier les visuels sélectionnés")
    def publish_action(self, _modeladmin, request, queryset):
        return self.publish(request, queryset)

    @admin.display(description="Dépublier les visuels sélectionnés")
    def unpublish_action(self, _modeladmin, request, queryset):
        return self.unpublish(request, queryset)

    def get_actions(self, request):
        self.actions = (self.publish_action, self.unpublish_action)
        return super().get_actions(request)

    def response_change(self, request, obj):
        if "_render" in request.POST:
            return self.render(request, obj)

        if "_publish" in request.POST:
            return self.publish(request, obj)

        if "_unpublish" in request.POST:
            return self.unpublish(request, obj)

        return super().response_change(request, obj)

    def get_urls(self):
        return [
            path(
                "<uuid:pk>/set-as-event-image/",
                self.admin_site.admin_view(self.set_as_event_image),
                name=f"{self.opts.app_label}_{self.opts.model_name}_set_as_event_image",
            ),
            path(
                "<uuid:pk>/preview/",
                self.admin_site.admin_view(self.preview),
                name=f"{self.opts.app_label}_{self.opts.model_name}_preview",
            ),
            path(
                "<uuid:pk>/render/",
                self.admin_site.admin_view(self.render),
                name=f"{self.opts.app_label}_{self.opts.model_name}_render",
            ),
            path(
                "<uuid:pk>/publish/",
                self.admin_site.admin_view(self.publish),
                name=f"{self.opts.app_label}_{self.opts.model_name}_publish",
            ),
            path(
                "<uuid:pk>/unpublish/",
                self.admin_site.admin_view(self.unpublish),
                name=f"{self.opts.app_label}_{self.opts.model_name}_unpublish",
            ),
        ] + super().get_urls()

    class Media:
        pass


@admin.register(models.EventThemeType)
class EventThemeTypeAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "event_subtype",
                    "event_request_validation_mode",
                    "calendar_link",
                    "map_link",
                )
            },
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
            {
                "fields": (
                    "event_image_template",
                    "event_asset_templates",
                )
            },
        ),
    )
    list_display = ("name", "event_subtype", "calendar_link", "map_link")
    list_filter = ("event_theme",)
    search_fields = ("name",)
    autocomplete_fields = ("event_subtype", "event_image_template")
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
            {
                "fields": (
                    "event_image_template",
                    "event_asset_templates",
                )
            },
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
    autocomplete_fields = ("event_theme_type", "event_image_template")
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
        return display_link(obj.event_theme_type_id)

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
        inlines.EventSpeakerPersonInline,
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
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "status",
                    "event_theme_type",
                    "event_theme",
                    "location_zip",
                    "location_city",
                    "location_country",
                    "datetimes",
                    "event_data",
                    "comment",
                    "event_field",
                )
            },
        ),
    )
    readonly_fields = (
        "event_theme_type",
        "event_theme",
        "event_field",
    )
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
        if not obj.is_pending:
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
        return display_link(obj.event)

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

    @admin.display(description="Type de thème d'événement")
    def event_theme_type(self, obj):
        if not obj:
            return "-"

        return display_link(obj.event_theme.event_theme_type)

    @admin.display(description="Événement")
    def event_field(self, obj):
        if obj and obj.event is not None:
            return display_link(obj.event)

        if obj and obj.has_manual_validation:
            return display_link(
                reverse(
                    f"admin:{self.opts.app_label}_{self.opts.model_name}_accept",
                    args=(obj.pk,),
                ),
                "Valider et créer l'événement",
                button=True,
            )

        return "-"

    def has_change_permission(self, request, obj=None):
        if obj and obj.event is not None:
            return False

        return super().has_change_permission(request, obj=obj)

    def get_urls(self):
        return [
            path(
                "<uuid:pk>/accept/",
                self.admin_site.admin_view(self.accept),
                name=f"{self.opts.app_label}_{self.opts.model_name}_accept",
            )
        ] + super().get_urls()

    def accept(self, request, pk):
        return views.accept_event_request(self, request, pk)

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
    readonly_fields = ("accepted",)
    date_hierarchy = "datetime"

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj is None:
            return readonly_fields
        return readonly_fields + self.createonly_fields

    @admin.display(description="Demande")
    def event_request_link(self, obj):
        display_link(obj.event_request)

    @admin.display(description="Intervenant·e")
    def event_speaker_link(self, obj):
        display_link(obj.event_speaker)

    def get_urls(self):
        return [
            path(
                "<uuid:pk>/accept/",
                self.admin_site.admin_view(self.accept_event_speaker_request),
                name=f"{self.opts.app_label}_{self.opts.model_name}_accept",
            ),
            path(
                "<uuid:pk>/unaccept/",
                self.admin_site.admin_view(self.unaccept_event_speaker_request),
                name=f"{self.opts.app_label}_{self.opts.model_name}_unaccept",
            ),
        ] + super().get_urls()

    def accept_event_speaker_request(self, request, pk):
        return views.accept_event_speaker_request(self, request, pk)

    def unaccept_event_speaker_request(self, request, pk):
        return views.unaccept_event_speaker_request(self, request, pk)

    @admin.display(description="Validation")
    def validation(self, obj):
        if obj.is_acceptable:
            return display_link(
                reverse(
                    "admin:event_requests_eventspeakerrequest_accept",
                    args=(obj.pk,),
                ),
                "Valider",
                button=True,
            )

        if obj.is_unacceptable:
            return display_link(
                reverse(
                    "admin:event_requests_eventspeakerrequest_unaccept",
                    args=(obj.pk,),
                ),
                "Annuler la validation",
                button=True,
            )

        return "-"

    class Media:
        pass
