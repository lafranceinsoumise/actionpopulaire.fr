from django.contrib import admin, messages
from django.db import transaction
from django.http import Http404, HttpResponseNotAllowed, HttpResponseRedirect
from django.shortcuts import redirect, get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse, path
from django.utils import timezone
from django.utils.html import escape, format_html, format_html_join

from agir.api.admin import admin_site
from agir.checks.models import CheckPayment
from agir.lib.admin import PersonLinkMixin
from agir.payments.actions.payments import (
    notify_status_change,
    change_payment_status,
    PaymentException,
)
from agir.payments.actions.subscriptions import terminate_subscription
from agir.payments.models import Subscription, Payment
from agir.payments.payment_modes import PAYMENT_MODES
from . import models


def notify_status_action(model_admin, request, queryset):
    for p in queryset:
        notify_status_change(p)


notify_status_action.short_description = "Renotifier le statut"


def change_payments_status_action(status, description):
    def action(modeladmin, request, queryset):
        try:
            with transaction.atomic():
                now = timezone.now().astimezone(timezone.utc).isoformat()

                for payment in queryset.filter(status=CheckPayment.STATUS_WAITING):
                    if not PAYMENT_MODES[payment.mode].can_admin:
                        raise PaymentException(
                            "Paiement n°{} ne peut pas être changé manuellement".format(
                                payment.id
                            )
                        )

                    change_payment_status(payment, status)
                    payment.events.append(
                        {
                            "change_status": status,
                            "date": now,
                            "origin": "payment_admin_action",
                        }
                    )
                    payment.save()
                    notify_status_change(payment)
        except PaymentException as exception:
            modeladmin.message_user(request, exception, level=messages.WARNING)

    # have to change the function name so that django admin see that they are different functions
    action.__name__ = f"change_to_{status}"
    action.short_description = description

    return action


class PaymentManagementAdminMixin:
    def change_status(self, request, pk, status):
        if status not in [
            Payment.STATUS_COMPLETED,
            Payment.STATUS_REFUSED,
            Payment.STATUS_CANCELED,
        ]:
            raise Http404()

        if request.method != "GET":
            return HttpResponseNotAllowed(permitted_methods="POST")

        payment = get_object_or_404(Payment, pk=pk)
        now = timezone.now().astimezone(timezone.utc).isoformat()

        with transaction.atomic():
            change_payment_status(payment, status)
            payment.events.append(
                {
                    "change_status": status,
                    "date": now,
                    "origin": self.opts.app_label + "_admin_change_button",
                }
            )
            payment.save(update_fields=["events"])
            notify_status_change(payment)

        return HttpResponseRedirect(
            reverse(
                "admin:{}_{}_change".format(self.opts.app_label, self.opts.model_name),
                args=[payment.pk],
            )
        )

    def status_buttons(self, payment):
        if payment.status != Payment.STATUS_WAITING:
            return "-"

        if not PAYMENT_MODES[payment.mode].can_admin:
            return format_html(
                '<a href="{}" target="_blank" class="button">Effectuer le paiement en ligne</a>',
                reverse("payment_page", args=[payment.pk]),
            )

        statuses = [
            (Payment.STATUS_COMPLETED, "Valider"),
            (Payment.STATUS_CANCELED, "Annuler"),
            (Payment.STATUS_REFUSED, "Refuser"),
        ]

        return format_html_join(
            " ",
            '<a href="{}" class="button">{}</a>',
            (
                (
                    reverse(
                        "admin:{}_{}_change_status".format(
                            self.opts.app_label, self.opts.model_name
                        ),
                        kwargs={"pk": payment.pk, "status": status},
                    ),
                    label,
                )
                for status, label in statuses
            ),
        )

    def change_mode(self, request, pk, mode):
        if mode not in PAYMENT_MODES:
            raise Http404()

        if request.method != "GET":
            return HttpResponseNotAllowed(permitted_methods="POST")

        payment = get_object_or_404(Payment, pk=pk)
        now = timezone.now().astimezone(timezone.utc).isoformat()

        with transaction.atomic():
            payment.mode = mode
            payment.events.append(
                {
                    "change_mode": mode,
                    "date": now,
                    "origin": self.opts.app_label + "_admin_change_mode",
                }
            )
            payment.save(update_fields=["mode", "events"])

        if not PAYMENT_MODES[mode].can_admin:
            return redirect("payment_page", payment.pk)

        return redirect(
            "admin:{}_{}_change".format(self.opts.app_label, self.opts.model_name),
            payment.pk,
        )

    def change_mode_buttons(self, payment):
        if (
            payment.status == Payment.STATUS_COMPLETED
            or payment.status == Payment.STATUS_CANCELED
        ):
            return payment.get_mode_display()

        return format_html_join(
            " ",
            '<a href="{}" class="button" {}>{}</a>',
            (
                (
                    reverse(
                        "admin:{}_{}_change_mode".format(
                            self.opts.app_label, self.opts.model_name
                        ),
                        kwargs={"pk": payment.pk, "mode": id},
                    ),
                    "disabled" if payment.mode == id else "",
                    mode.label,
                )
                for id, mode in PAYMENT_MODES.items()
            ),
        )

    change_mode_buttons.short_description = "Mode de paiement"

    def get_urls(self):
        return [
            path(
                "<int:pk>/change/<int:status>/",
                admin_site.admin_view(self.change_status),
                name="{}_{}_change_status".format(
                    self.opts.app_label, self.opts.model_name
                ),
            ),
            path(
                "<int:pk>/change_mode/<str:mode>/",
                admin_site.admin_view(self.change_mode),
                name="{}_{}_change_mode".format(
                    self.opts.app_label, self.opts.model_name
                ),
            ),
        ] + super().get_urls()

    status_buttons.short_description = "Actions"


@admin.register(models.Payment, site=admin_site)
class PaymentAdmin(PaymentManagementAdminMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "get_type_display",
        "person",
        "email",
        "first_name",
        "last_name",
        "get_price_display",
        "status",
        "created",
        "get_mode_display",
    )
    readonly_fields = (
        "get_type_display",
        "person",
        "email",
        "first_name",
        "last_name",
        "get_price_display",
        "phone_number",
        "location_address1",
        "location_address2",
        "location_zip",
        "location_city",
        "location_country",
        "meta",
        "events",
        "status",
        "change_mode_buttons",
        "status_buttons",
    )
    fields = readonly_fields
    list_filter = ("status", "type", "mode")
    search_fields = ("email", "first_name", "last_name", "=id")

    actions = [
        notify_status_action,
        change_payments_status_action(Payment.STATUS_COMPLETED, "Marquer comme reçu"),
        change_payments_status_action(Payment.STATUS_CANCELED, "Marqué comme annulé"),
    ]


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
