from django.contrib import admin
from django.db.models import TextField
from django.forms import Textarea
from django.urls import reverse

from agir.event_requests import models
from agir.events.models import Event
from agir.lib.admin.inlines import NonrelatedTabularInline
from agir.lib.admin.utils import display_link
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
    fields = ("name", "file", "published", "is_image")
    readonly_fields = ("published", "is_image")
    show_change_link = True
    extra = 0

    @admin.display(description="Image de l'événement", boolean=True)
    def is_image(self, obj):
        return obj.is_event_image


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
        if not has_change_permission:
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
