from django.contrib import admin

from agir.donations.models import (
    MonthlyAllocation,
    AccountOperation,
)
from agir.payments import models


class PaymentInline(admin.TabularInline):
    model = models.Payment
    show_change_link = True
    can_delete = False
    extra = 0
    fields = readonly_fields = (
        "created",
        "get_price_display",
        "status",
        "get_allocations_display",
    )

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj):
        return False


class MonthlyAllocationInline(admin.TabularInline):
    model = MonthlyAllocation
    show_change_link = True
    can_delete = False
    extra = 0
    fields = readonly_fields = (
        "type",
        "get_amount_display",
        "group",
        "departement",
        "subscription",
    )

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj):
        return False


class AccountOperationInline(admin.TabularInline):
    model = AccountOperation
    show_change_link = True
    can_delete = False
    extra = 0
    fields = readonly_fields = ("get_amount_display", "source", "destination")

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj):
        return False
