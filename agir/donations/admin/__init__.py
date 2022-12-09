from django.contrib import admin
from django.urls import reverse, path
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from agir.donations.admin.actions import (
    export_spending_requests_to_xlsx,
    export_spending_requests_to_csv,
)
from agir.donations.admin.filters import (
    MonthlyAllocationGroupFilter,
    MonthlyAllocationSubscriptionPersonFilter,
)
from agir.donations.admin.forms import HandleRequestForm
from agir.donations.admin.views import HandleRequestView
from agir.donations.models import (
    SpendingRequest,
    Document,
    Operation,
    MonthlyAllocation,
    DepartementOperation,
    CNSOperation,
)
from agir.lib.display import display_price


def mark_as_paid(model_admin, request, queryset):
    queryset.update(status=SpendingRequest.STATUS_PAID)


mark_as_paid.short_description = _("Indiquer ces demandes comme payées")


class DocumentInline(admin.TabularInline):
    model = Document
    extra = 0
    can_delete = False


class RequestStatusFilter(admin.SimpleListFilter):
    title = _("Statut")

    parameter_name = "status"

    def lookups(self, request, model_admin):
        return (
            ("group", _("En attente du groupe")),
            ("review", _("À revoir")),
            ("to_pay", _("À payer")),
            ("finished", _("Terminées")),
        )

    def queryset(self, request, queryset):
        if self.value() == "group":
            return queryset.filter(status__in=SpendingRequest.STATUS_NEED_ACTION)
        elif self.value() == "review":
            return queryset.filter(status=SpendingRequest.STATUS_AWAITING_REVIEW)
        elif self.value() == "to_pay":
            return queryset.filter(status=SpendingRequest.STATUS_TO_PAY)
        elif self.value() == "finished":
            return queryset.filter(
                status__in=[SpendingRequest.STATUS_PAID, SpendingRequest.STATUS_REFUSED]
            )
        else:
            return queryset.filter()


@admin.register(SpendingRequest)
class SpendingRequestAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "status",
        "spending_date",
        "group",
        "show_amount",
        "category",
        "spending_request_actions",
        "modified",
    ]
    ordering = ("-modified",)
    sortable_by = ("title", "spending_date", "show_amount")
    search_fields = ("id", "title", "group__name")
    list_filter = (RequestStatusFilter,)
    actions = (
        export_spending_requests_to_csv,
        export_spending_requests_to_xlsx,
        mark_as_paid,
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "id",
                    "title",
                    "status",
                    "spending_date",
                    "amount",
                    "created",
                    "modified",
                )
            },
        ),
        (_("Groupe et événement"), {"fields": ("group", "event")}),
        (
            _("Détails de la demande"),
            {
                "fields": (
                    "category",
                    "category_precisions",
                    "explanation",
                    "provider",
                    "iban",
                )
            },
        ),
    )

    readonly_fields = ("created", "modified", "show_amount")
    autocomplete_fields = ("group", "event")
    inlines = (DocumentInline,)

    def show_amount(self, obj):
        return display_price(obj.amount)

    show_amount.short_description = "Montant"
    show_amount.admin_order_field = "amount"

    def spending_request_actions(self, obj):
        return format_html(
            '<a href="{url}">{text}</a>',
            url=reverse("admin:donations_spendingrequest_review", args=[obj.pk]),
            text="Traiter",
        )

    spending_request_actions.short_description = "Actions"

    def get_urls(self):
        return [
            path(
                "<uuid:pk>/review/",
                self.admin_site.admin_view(HandleRequestView.as_view(model_admin=self)),
                name="donations_spendingrequest_review",
            )
        ] + super().get_urls()


@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    list_display = ("group", "amount", "payment", "created")
    fields = ("group", "amount")
    autocomplete_fields = ("group",)

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(DepartementOperation)
class DepartementOperationAdmin(admin.ModelAdmin):
    list_display = ("departement", "amount", "payment", "created")
    fields = ("departement", "amount")

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(CNSOperation)
class CNSOperationAdmin(admin.ModelAdmin):
    list_display = ("amount", "payment", "created")
    fields = ("amount",)

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(MonthlyAllocation)
class MonthlyAllocationAdmin(admin.ModelAdmin):
    list_display = ("__str__", "type", "group", "departement", "amount", "subscription")
    list_filter = (
        MonthlyAllocationGroupFilter,
        MonthlyAllocationSubscriptionPersonFilter,
        "subscription__status",
    )
    readonly_fields = ("type", "group", "departement", "subscription", "amount")

    class Media:
        pass
