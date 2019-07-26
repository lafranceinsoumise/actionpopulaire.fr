from django.contrib import admin
from django.http import Http404
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse, path
from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe

from agir.api.admin import admin_site
from agir.lib.admin import PersonLinkMixin
from agir.payments.actions.payments import notify_status_change
from agir.payments.actions.subscriptions import terminate_subscription
from agir.payments.models import Subscription
from agir.payments.payment_modes import PAYMENT_MODES
from agir.system_pay import AbstractSystemPayPaymentMode
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
    search_fields = ("email", "first_name", "last_name", "=id")

    actions = (notify_status_action,)


@admin.register(models.Subscription, site=admin_site)
class SubscriptionAdmin(PersonLinkMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "person_link",
        "price",
        "type",
        "status",
        "created",
        "mode",
        "day_of_month",
    )
    readonly_fields = (
        "mode",
        "type",
        "person_link",
        "price",
        "status",
        "terminate_button",
    )
    fields = readonly_fields
    list_filter = ("status", "mode")
    search_fields = ("person__search", "=id")

    def get_urls(self):
        return [
            path(
                "<int:subscription_pk>/terminate/",
                admin_site.admin_view(self.terminate_view),
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
                pk=subscription_pk, status=Subscription.STATUS_COMPLETED
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
