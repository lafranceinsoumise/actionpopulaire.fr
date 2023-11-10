from agir.donations.allocations import get_allocation_list
from django.contrib import admin, messages
from django.contrib.admin.views.main import ChangeList
from django.db import transaction
from django.db.models import Sum
from django.http import Http404
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse, path
from django.utils.html import escape, format_html
from rangefilter.filters import DateRangeFilter

from agir.lib.admin.panels import PersonLinkMixin, AddRelatedLinkMixin
from agir.lib.admin.utils import display_json_details
from agir.payments import models
from agir.payments.actions.payments import (
    log_payment_event,
)
from agir.payments.actions.subscriptions import terminate_subscription
from agir.payments.admin.actions import (
    notify_status_action,
    change_payments_status_action,
)
from agir.payments.admin.forms import PaymentAdminForm
from agir.payments.admin.inlines import (
    PaymentInline,
    MonthlyAllocationInline,
)
from agir.payments.admin.mixins import PaymentManagementAdminMixin
from agir.payments.models import Subscription, Payment


class PaymentChangeList(ChangeList):
    def get_results(self, *args, **kwargs):
        super().get_results(*args, **kwargs)
        self.sum = self.queryset.aggregate(sum=Sum("price"))["sum"] or 0


@admin.register(models.Payment)
class PaymentAdmin(PaymentManagementAdminMixin, AddRelatedLinkMixin, admin.ModelAdmin):
    form = PaymentAdminForm
    list_display = (
        "__str__",
        "get_type_display",
        "person",
        "email",
        "first_name",
        "last_name",
        "get_price_display",
        "get_allocations_display",
        "status",
        "created",
        "get_mode_display",
    )
    readonly_fields = (
        "id",
        "created",
        "modified",
        "status",
        "person",
        "email",
        "first_name",
        "last_name",
        "phone_number",
        "location_address1",
        "location_address2",
        "location_zip",
        "location_city",
        "location_country",
        "meta_data",
        "event_data",
        "status",
        "change_mode_buttons",
        "status_buttons",
        "get_price_display",
        "get_allocations_display",
        "cancel_or_refund_button",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "id",
                    "created",
                    "modified",
                    "person_link",
                    "status",
                    "price",
                    "get_allocations_display",
                    "type",
                    "change_mode_buttons",
                    "status_buttons",
                    "cancel_or_refund_button",
                )
            },
        ),
        (
            "Informations de facturation",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "phone_number",
                    "location_address1",
                    "location_address2",
                    "location_zip",
                    "location_city",
                    "location_country",
                )
            },
        ),
        (
            "Informations supplémentaires",
            {
                "fields": (
                    "meta_data",
                    "event_data",
                )
            },
        ),
    )

    @admin.display(description="Meta", ordering="meta")
    def meta_data(self, obj):
        return display_json_details(
            {
                **obj.meta,
                "allocations": get_allocation_list(
                    obj.meta.get("allocations", []), with_labels=False
                ),
            },
            "Données de paiement",
            is_open=True,
        )

    @admin.display(description="Événements", ordering="events")
    def event_data(self, obj):
        return display_json_details(obj.events, "Événements de paiement", is_open=True)

    def get_changelist(self, request, **kwargs):
        return PaymentChangeList

    list_filter = ("status", "type", "mode", ("created", DateRangeFilter))
    search_fields = ("email", "first_name", "last_name", "=id")

    actions = [
        notify_status_action,
        change_payments_status_action(Payment.STATUS_COMPLETED, "Marquer comme reçu"),
        change_payments_status_action(Payment.STATUS_CANCELED, "Marqué comme annulé"),
    ]

    def save_form(self, request, form, change):
        with transaction.atomic():
            payment = form.instance
            if (
                change
                and "price" in form.changed_data
                and payment.price != form["price"].initial
            ):
                log_payment_event(
                    payment,
                    event="price_change",
                    new_price=payment.price,
                    old_price=form["price"].initial,
                    origin=self.opts.app_label + "_admin_change_price",
                    user=request.user,
                )
                self.message_user(
                    request, "Le montant a bien été modifié.", messages.SUCCESS
                )

            return super().save_form(request, form, change)

    def has_add_permission(self, request):
        return False


@admin.register(models.Subscription)
class SubscriptionAdmin(PersonLinkMixin, admin.ModelAdmin):
    list_display = (
        "__str__",
        "person_link",
        "get_price_display",
        "get_allocations_display",
        "type",
        "status",
        "created",
        "mode",
        "day_of_month",
        "effect_date",
        "end_date",
        "metadata",
    )
    readonly_fields = (
        "id",
        "mode",
        "type",
        "person_link",
        "get_price_display",
        "get_allocations_display",
        "status",
        "terminate_button",
        "effect_date",
        "end_date",
        "day_of_month",
        "metadata",
    )
    fields = readonly_fields
    list_filter = ("status", "mode", ("created", DateRangeFilter))
    search_fields = ("person__search", "=id")
    inlines = (
        MonthlyAllocationInline,
        PaymentInline,
    )

    def get_changelist(self, request, **kwargs):
        return PaymentChangeList

    def metadata(self, subscription):
        if not subscription:
            return "-"

        return display_json_details(
            {
                **subscription.meta,
                "allocations": get_allocation_list(
                    subscription.meta.get("allocations", []), with_labels=False
                ),
            },
            "Données de paiement",
            is_open=True,
        )

    def get_urls(self):
        return [
            path(
                "<int:subscription_pk>/terminate/",
                self.admin_site.admin_view(self.terminate_view),
                name="payments_subscription_terminate",
            )
        ] + super().get_urls()

    def terminate_button(self, subscription):
        if subscription._state.adding:
            return "-"
        else:
            return format_html(
                '<a href="{}" class="button">Désactiver l\'abonnement</a>',
                reverse(
                    "admin:payments_subscription_terminate", args=(subscription.pk,)
                ),
            )

    def terminate_view(self, request, subscription_pk):
        try:
            subscription = Subscription.objects.get(
                pk=subscription_pk, status=Subscription.STATUS_ACTIVE
            )
        except Subscription.DoesNotExist:
            raise Http404()

        if request.method == "POST":
            terminate_subscription(subscription)

            return redirect("admin:payments_subscription_change", subscription_pk)

        context = {
            "title": "Désactiver le paiment récurent: %s" % escape(subscription_pk),
            "is_popup": True,
            "opts": self.model._meta,
            "subscription": subscription,
            "change": True,
            "add": False,
            "save_as": False,
            "show_save": True,
            "has_delete_permission": self.has_delete_permission(request, subscription),
            "has_add_permission": self.has_add_permission(request),
            "has_change_permission": self.has_change_permission(request, subscription),
            "has_view_permission": self.has_view_permission(request, subscription),
            "has_editable_inline_admin_formsets": False,
        }
        context.update(self.admin_site.each_context(request))

        request.current_app = self.admin_site.name

        return TemplateResponse(
            request, "admin/subscriptions/terminate_subscription.html", context
        )
