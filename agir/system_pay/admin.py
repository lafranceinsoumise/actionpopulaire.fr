from django.contrib import admin

from . import models


@admin.register(models.SystemPayTransaction)
class SystemPayTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "payment",
        "subscription",
        "destination",
        "person",
        "status",
        "webhook_calls",
        "alias_identifier",
    )
    readonly_fields = (
        "id",
        "payment",
        "is_refund",
        "subscription",
        "destination",
        "person",
        "status",
        "webhook_calls",
        "alias",
    )
    fields = readonly_fields
    list_filter = ("status",)
    search_fields = ("payment__email", "payment__person__emails__address__iexact")

    def destination(self, obj):
        if obj.payment is not None:
            return obj.payment.mode

        if obj.subscription is not None:
            return obj.subscription.mode

    def person(self, obj):
        if obj.payment is not None:
            return obj.payment.person

        if obj.subscription is not None:
            return obj.subscription.person

    def alias_identifier(self, obj):
        if obj.alias is not None:
            return obj.alias.identifier

        return "-"
