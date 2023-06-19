from agir.donations.models import (
    MonthlyAllocation,
    Operation,
    DepartementOperation,
    CNSOperation,
)
from agir.payments import models
from django.contrib import admin


class PaymentInline(admin.TabularInline):
    model = models.Payment
    show_change_link = False
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


class CNSOperationInline(admin.TabularInline):
    model = CNSOperation
    show_change_link = True
    can_delete = False
    extra = 0
    fields = readonly_fields = ("get_amount_display",)

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj):
        return False


class DepartementOperationInline(CNSOperationInline):
    model = DepartementOperation
    fields = readonly_fields = (
        "get_amount_display",
        "departement",
    )


class OperationInline(CNSOperationInline):
    verbose_name = "Opération de groupe"
    verbose_name_plural = "Opérations de groupe"
    model = Operation
    fields = readonly_fields = ("get_amount_display", "group")
