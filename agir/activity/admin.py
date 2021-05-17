from django.contrib import admin
from django.utils.html import format_html

from agir.activity.models import Activity, Announcement


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ("timestamp", "type", "recipient", "status", "pushed")}),
        (
            "Éléments liés",
            {"fields": ("event", "supportgroup", "individual", "announcement", "meta")},
        ),
        ("Création et modification", {"fields": ("created", "modified")}),
    )
    list_display = ("type", "timestamp", "recipient", "status", "pushed")
    list_filter = ("type", "status")

    readonly_fields = ("created", "modified", "pushed")
    autocomplete_fields = (
        "recipient",
        "event",
        "supportgroup",
        "individual",
    )

    search_fields = [
        "recipient__display_name",
        "recipient__first_name",
        "recipient__last_name",
    ]


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    MINIATURE_BOX = '<div style="margin: 0 10px;"><h4 style="margin:0;padding:0;">{type}</h4><img src="{link}"></div>'

    fieldsets = (
        ("Contenu", {"fields": ("title", "link", "content", "image", "miniatures")}),
        (
            "Conditions d'affichage",
            {
                "fields": (
                    "segment",
                    "start_date",
                    "end_date",
                    "priority",
                    "custom_display",
                )
            },
        ),
        ("Statistiques", {"fields": ("affichages", "clics")}),
    )

    readonly_fields = ["miniatures", "affichages", "clics"]
    list_display = ("__str__", "start_date", "end_date")
    autocomplete_fields = ("segment",)

    def miniatures(self, obj):
        if obj is None:
            return "-"

        mobile = format_html(
            self.MINIATURE_BOX, type="mobile", link=obj.image.mobile.url
        )
        desktop = format_html(
            self.MINIATURE_BOX, type="desktop", link=obj.image.desktop.url
        )

        return format_html(
            '<div style="display:flex;">{mobile}{desktop}</div>',
            mobile=mobile,
            desktop=desktop,
        )

    miniatures.short_description = "Affichage de l'image selon l'environnement"

    def affichages(self, obj):
        if obj.id:
            return obj.activities.filter(
                status__in=(Activity.STATUS_DISPLAYED, Activity.STATUS_INTERACTED)
            ).count()
        return "-"

    affichages.short_description = "Nombre d'affichages uniques"

    def clics(self, obj):
        if obj.id:
            return obj.activities.filter(status=Activity.STATUS_INTERACTED).count()

    clics.short_description = "Nombre de clics uniques"
