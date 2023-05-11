import os

from django.contrib import admin
from django.db.models import TextField
from django.forms import Textarea
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from agir.event_requests import models
from agir.events.models import Event
from agir.lib.admin.inlines import NonrelatedTabularInline
from agir.lib.admin.utils import display_link, admin_url
from agir.people.models import Person


class EventAssetTemplateInline(NonrelatedTabularInline):
    verbose_name = "template de visuel"
    verbose_name_plural = "templates de visuels"
    model = models.EventAssetTemplate
    fields = ("name", "file", "target_format")
    extra = 0
    show_change_link = True
    can_delete = False

    def get_form_queryset(self, obj):
        return obj.event_asset_templates.all()

    def save_new_instance(self, parent, instance):
        instance.save()
        parent.event_asset_templates.add(instance)


class EventAssetInline(admin.TabularInline):
    verbose_name = "visuel de l'événement"
    verbose_name_plural = "visuels de l'événement"
    model = models.EventAsset
    fields = (
        "name",
        "file",
        "image",
        "render",
        "publishing",
    )
    readonly_fields = (
        "thumbnail",
        "image",
        "render",
        "publishing",
    )
    show_change_link = True
    extra = 0

    @admin.display(description="Génération")
    def render(self, obj):
        if obj and obj.renderable:
            return format_html(
                '<a href="{}" class="button" title="Régénérer le visuel">⟳ Régénérer</a>'
                "<p class='help' style='margin:0;padding:8px 0 0;font-size:0.75rem;'>"
                "<strong>⚠ Le visuel existant sera définitivement supprimé</strong>"
                "</p>",
                admin_url(
                    f"{self.opts.app_label}_{self.opts.model_name}_render",
                    args=[obj.id],
                ),
            )

        return "-"

    @admin.display(description="Image de bannière")
    def image(self, obj):
        if obj.is_event_image:
            return mark_safe('<img src="/static/admin/img/icon-yes.svg" alt="True">')

        if obj.is_event_image_candidate:
            return format_html(
                '<a href="{}" class="button" title="Utiliser comme image de bannière">🖼️ Utiliser comme image</a>'
                "<p class='help' style='margin:0;padding:8px 0 0;font-size:0.75rem;'>"
                "<strong>⚠ L'image existante sera définitivement supprimée</strong>"
                "</p>",
                admin_url(
                    f"{self.opts.app_label}_{self.opts.model_name}_set_as_event_image",
                    args=[obj.id],
                ),
            )
        return mark_safe('<img src="/static/admin/img/icon-no.svg" alt="False">')

    @admin.display(description="Aperçu")
    def thumbnail(self, obj):
        if obj.is_event_image or obj.is_event_image_candidate:
            src = obj.file.url
        else:
            src = "https://placehold.co/80x80/e9e1ff/cbbfec?font=playfair-display&text="
            if obj.file.name:
                _, ext = os.path.splitext(obj.file.name)
                src += ext.lower().replace(".", "")
            else:
                src += "…"

        return format_html(
            '<img style="max-height:160px;max-width:160px;width:auto;height:auto;" src="{}" alt={} />',
            src,
            obj.name,
        )

    @admin.display(description="Publication")
    def publishing(self, obj):
        if obj and not obj.published:
            return format_html(
                "<a href='{}' class='button'>✔ Publier</a>"
                "<p class='help' style='margin:0;padding:8px 0 0;font-size:0.75rem;'>"
                "Les organisateur·ices recevront une notification et pourront accèder au visuel "
                "dans le volet de gestion de la page de l'événement"
                "</p>",
                admin_url(
                    f"{self.opts.app_label}_{self.opts.model_name}_publish",
                    args=[obj.id],
                ),
            )

        if obj and obj.published:
            return format_html(
                "<a href='{}' class='button'>✖ Dépublier</a>",
                admin_url(
                    f"{self.opts.app_label}_{self.opts.model_name}_unpublish",
                    args=[obj.id],
                ),
            )

        return "-"

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if obj and not obj._state.adding:
            for asset in obj.event_assets.all():
                if asset.is_event_image_candidate:
                    return "thumbnail", *fields
        return fields


class EventThemeInline(admin.TabularInline):
    verbose_name = "thème"
    verbose_name_plural = "thèmes"
    model = models.EventTheme
    extra = 0
    show_change_link = True
    fields = ("name",)
    exclude = ("description", "event_asset_templates")


class EventSpeakerThemeInline(admin.TabularInline):
    verbose_name = "thème"
    verbose_name_plural = "thèmes"
    model = models.EventSpeaker.event_themes.through
    extra = 0
    can_delete = False
    show_change_link = True

    def has_change_permission(self, request, obj=None):
        return False


class EventThemeSpeakerInline(admin.TabularInline):
    verbose_name = "intervenant·e"
    verbose_name_plural = "intervenant·es"
    model = models.EventSpeaker.event_themes.through
    extra = 0
    can_delete = False
    show_change_link = True
    autocomplete_fields = ("eventspeaker",)

    def has_change_permission(self, request, obj=None):
        return False


class EventSpeakerRequestInline(admin.TabularInline):
    verbose_name = "demandes de disponibilité"
    verbose_name_plural = "demandes de disponibilité"
    model = models.EventSpeakerRequest
    extra = 0
    can_delete = False
    show_change_link = False
    fields = (
        "event_speaker",
        "datetime",
        "available",
        "comment",
        "accepted",
        "validation",
    )
    readonly_fields = (
        "event_speaker",
        "datetime",
        "accepted",
        "validation",
    )
    ordering = ("datetime", "-accepted", "-available")
    formfield_overrides = {
        TextField: {"widget": Textarea(attrs={"rows": 1})},
    }

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        has_change_permission = super().has_change_permission(request, obj)

        if not obj or not has_change_permission:
            return False

        return False == (
            obj.event_theme.event_theme_type.has_event_speaker_request_emails
        )

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
                "Annuler",
                button=True,
            )

        return "-"


class EventSpeakerEventInline(NonrelatedTabularInline):
    verbose_name = "événement"
    verbose_name_plural = "événements"
    model = Event
    extra = 0
    can_add = False
    can_delete = False
    show_change_link = True
    fields = readonly_fields = (
        "name",
        "visibility",
        "get_display_date",
        "location",
        "created",
    )

    def get_form_queryset(self, obj):
        return obj.events.all()

    def save_new_instance(self, parent, instance):
        instance.save()
        parent.events.add(instance)

    def has_add_permission(self, request, obj):
        return False

    @admin.display(description="Lieu", ordering="location_city")
    def location(self, obj):
        return f"{obj.location_zip} {obj.location_city}, {obj.location_country.name}"


class EventSpeakerUpcomingEventInline(EventSpeakerEventInline):
    verbose_name = "événement à venir"
    verbose_name_plural = "événements à venir"
    ordering = ("start_time",)

    def get_form_queryset(self, obj):
        return obj.events.upcoming()


class EventSpeakerPastEventInline(EventSpeakerEventInline):
    verbose_name = "dernier événement"
    verbose_name_plural = "derniers événements"
    ordering = ("-start_time",)
    max_num = 10

    def get_form_queryset(self, obj):
        return obj.events.past()


class EventSpeakerPersonInline(NonrelatedTabularInline):
    model = Person
    verbose_name = "personne"
    verbose_name_plural = "personne"
    extra = 0
    can_add = False
    can_delete = False
    show_change_link = False
    readonly_fields = ("display_email",)
    fields = (
        "display_email",
        "first_name",
        "last_name",
        "image",
    )

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_form_queryset(self, obj):
        return self.model.objects.filter(id=obj.person_id)

    def save_new_instance(self, parent, instance):
        instance.save()

    @admin.display(description="E-mail d'affichage")
    def display_email(self, obj):
        return obj.display_email
