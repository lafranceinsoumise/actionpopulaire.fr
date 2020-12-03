from django.contrib import admin

from agir.activity.models import Activity


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ("timestamp", "type", "recipient", "status")}),
        ("Éléments liés", {"fields": ("event", "supportgroup", "individual", "meta")}),
        ("Création et modification", {"fields": ("created", "modified")}),
    )
    list_display = ("type", "timestamp", "recipient", "status")

    readonly_fields = ("created", "modified")
