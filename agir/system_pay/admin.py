import json

from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from . import models
from ..lib.admin.utils import display_link


@admin.register(models.SystemPayTransaction)
class SystemPayTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "payment_link",
        "destination",
        "person",
        "status",
        "alias_identifier",
        "payment_events",
    )
    readonly_fields = (
        "id",
        "payment",
        "is_refund",
        "subscription",
        "destination",
        "person",
        "status",
        "payment_events",
        "alias",
    )
    fields = readonly_fields
    list_filter = ("status",)
    search_fields = ("payment__email", "payment__person__emails__address__iexact")

    @admin.display(description="Paiement/Abonnement")
    def payment_link(self, obj):
        if obj.payment is not None:
            return display_link(obj.payment)

        if obj.subscription is not None:
            return display_link(obj.subscription)

    @admin.display(description="Mode")
    def destination(self, obj):
        if obj.payment is not None:
            return obj.payment.mode

        if obj.subscription is not None:
            return obj.subscription.mode

    @admin.display(description="Personne")
    def person(self, obj):
        if obj.payment is not None:
            return display_link(obj.payment.person)

        if obj.subscription is not None:
            return display_link(obj.subscription.person)

    @admin.display(description="Alias")
    def alias_identifier(self, obj):
        if obj.alias is not None:
            return obj.alias.identifier

        return "-"

    @admin.display(description="Événements de paiement", ordering="webhook_calls")
    def payment_events(self, obj):
        if not obj or not obj.webhook_calls:
            return "-"

        return format_html(
            "<details>"
            "<summary style='cursor:pointer;'>Événements de paiement</summary>"
            "<pre>{}</pre>"
            "</details>",
            mark_safe(json.dumps(obj.webhook_calls, indent=2)),
        )
