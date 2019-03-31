from django.contrib import admin

from agir.api.admin import admin_site
from agir.payments.actions import notify_status_change
from . import models


def notify_status_action(model_admin, request, queryset):
    for p in queryset:
        notify_status_change(p)


notify_status_action.short_description = "Renotifier le statut"


@admin.register(models.Payment, site=admin_site)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "type",
        "person",
        "email",
        "first_name",
        "last_name",
        "price",
        "status",
        "created",
        "mode",
    )
    readonly_fields = (
        "type",
        "mode",
        "person",
        "email",
        "first_name",
        "last_name",
        "price",
        "phone_number",
        "location_address1",
        "location_address2",
        "location_zip",
        "location_city",
        "location_country",
        "meta",
        "events",
    )
    fields = readonly_fields + ("status",)
    list_filter = ("status", "type", "mode")
    search_fields = ("email", "person__emails__address__iexact")

    actions = (notify_status_action,)
