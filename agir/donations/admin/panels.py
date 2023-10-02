from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.db.models import Sum
from django.urls import reverse, path
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from rangefilter.filters import DateRangeFilter
from reversion.admin import VersionAdmin

from agir.donations.admin import inlines, filters
from agir.donations.admin.actions import (
    export_spending_requests_to_xlsx,
    export_spending_requests_to_csv,
    mark_spending_request_as_paid,
)
from agir.donations.admin.filters import (
    MonthlyAllocationGroupFilter,
    MonthlyAllocationSubscriptionPersonFilter,
)
from agir.donations.admin.views import HandleRequestView
from agir.donations.models import (
    SpendingRequest,
    Operation,
    MonthlyAllocation,
    DepartementOperation,
    CNSOperation,
)
from agir.lib.admin.utils import display_link
from agir.lib.display import display_price
from agir.lib.templatetags.display_lib import display_price_in_cent


@admin.register(SpendingRequest)
class SpendingRequestAdmin(VersionAdmin):
    list_display = [
        "title",
        "status",
        "category",
        "show_amount",
        "group_link",
        "spending_date",
        "modified",
        "spending_request_actions",
    ]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "id",
                    "title",
                    "timing",
                    "campaign",
                    "spending_date",
                    "amount",
                    "status",
                    "creator",
                    "created",
                    "modified",
                    "spending_request_actions",
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
                    "bank_account_name",
                    "bank_account_iban",
                    "bank_account_bic",
                    "bank_account_rib",
                )
            },
        ),
        (
            _("Informations de contact"),
            {"fields": ("contact_name", "contact_email", "contact_phone")},
        ),
    )
    readonly_fields = (
        "id",
        "creator",
        "created",
        "modified",
        "show_amount",
        "spending_request_actions",
        "group_link",
    )
    autocomplete_fields = ("group", "event")
    inlines = (inlines.DocumentInline, inlines.DeletedDocumentInline)
    ordering = ("-modified",)
    sortable_by = ("title", "spending_date", "show_amount")
    search_fields = ("id", "title", "group__name", "event__name")
    list_filter = (
        filters.RequestStatusFilter,
        filters.SupportGroupFilter,
        "category",
        "timing",
        ("spending_date", DateRangeFilter),
    )
    actions = (
        export_spending_requests_to_csv,
        export_spending_requests_to_xlsx,
        mark_spending_request_as_paid,
    )

    class Media:
        pass

    @admin.display(description="Groupe", ordering="group")
    def group_link(self, obj):
        return display_link(obj.group)

    @admin.display(description="Montant", ordering="amount")
    def show_amount(self, obj):
        return display_price(obj.amount)

    @admin.display(description="Actions")
    def spending_request_actions(self, obj):
        if not obj or not obj.pk:
            return "-"

        return display_link(
            reverse("admin:donations_spendingrequest_review", args=[obj.pk]),
            text="📝 Traiter la demande",
            button=True,
        )

    def get_urls(self):
        return [
            path(
                "<uuid:pk>/review/",
                self.admin_site.admin_view(HandleRequestView.as_view(model_admin=self)),
                name="donations_spendingrequest_review",
            )
        ] + super().get_urls()


class OperationChangeList(ChangeList):
    def get_results(self, *args, **kwargs):
        super().get_results(*args, **kwargs)
        self.sum = self.queryset.aggregate(sum=Sum("amount"))["sum"] or 0


class OperationAdminMixin(admin.ModelAdmin):
    change_list_template = "admin/operations/change_list.html"
    list_display = ("amount_display", "payment_link", "created", "comment")
    list_filter = (
        ("created", admin.DateFieldListFilter),
        ("created", DateRangeFilter),
    )
    search_fields = ("comment",)
    fields = ("amount", "payment_link", "comment")
    readonly_fields = ("payment_link",)

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def get_changelist(self, request, **kwargs):
        return OperationChangeList

    @admin.display(description="Paiement", ordering="payment")
    def payment_link(self, obj):
        if not obj or not obj.payment:
            return "-"

        return format_html(
            '<a href="{url}">{text}</a>',
            url=reverse("admin:payments_payment_change", args=[obj.payment.pk]),
            text=str(obj.payment),
        )

    @admin.display(description="Montant net", ordering="amount")
    def amount_display(self, obj):
        if not obj or not obj.amount:
            return "-"

        return display_price_in_cent(obj.amount)

    class Media:
        pass


@admin.register(Operation)
class OperationAdmin(OperationAdminMixin):
    list_display = ("group", "amount_display", "payment_link", "created", "comment")
    list_filter = (
        filters.SupportGroupFilter,
        ("created", admin.DateFieldListFilter),
        ("created", DateRangeFilter),
    )
    search_fields = ("group__name",)
    fields = ("group", "amount", "payment_link", "comment")
    autocomplete_fields = ("group",)


@admin.register(DepartementOperation)
class DepartementOperationAdmin(OperationAdminMixin):
    list_display = (
        "departement",
        "amount_display",
        "payment_link",
        "created",
        "comment",
    )
    list_filter = (
        filters.DepartementFilter,
        ("created", admin.DateFieldListFilter),
        ("created", DateRangeFilter),
    )
    search_fields = ("departement",)
    fields = ("departement", "amount", "payment_link", "comment")


@admin.register(CNSOperation)
class CNSOperationAdmin(OperationAdminMixin):
    pass


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
