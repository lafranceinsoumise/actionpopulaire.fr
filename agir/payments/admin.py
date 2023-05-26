from django import forms
from django.contrib import admin, messages
from django.contrib.admin.views.main import ChangeList
from django.core.exceptions import SuspiciousOperation
from django.db import transaction
from django.db.models import Sum
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse, path
from django.utils.html import escape, format_html, format_html_join
from rangefilter.filters import DateRangeFilter

from agir.checks.models import CheckPayment
from agir.donations.form_fields import MoneyField
from agir.lib.admin.panels import PersonLinkMixin, AddRelatedLinkMixin
from agir.lib.utils import front_url
from agir.system_pay import SystemPayError
from . import models
from .actions.payments import (
    notify_status_change,
    change_payment_status,
    PaymentException,
    cancel_or_refund_payment,
    log_payment_event,
)
from .actions.subscriptions import terminate_subscription
from .models import Subscription, Payment
from .payment_modes import PAYMENT_MODES
from .types import PAYMENT_TYPES, get_payment_choices
from ..lib.admin.utils import display_json_details


def notify_status_action(model_admin, request, queryset):
    for p in queryset:
        notify_status_change(p)


notify_status_action.short_description = "Renotifier le statut"


def change_payments_status_action(status, description):
    def action(modeladmin, request, queryset):
        try:
            with transaction.atomic():
                for payment in queryset.filter(status=CheckPayment.STATUS_WAITING):
                    if not PAYMENT_MODES[payment.mode].can_admin:
                        raise PaymentException(
                            "Paiement n°{} ne peut pas être changé manuellement".format(
                                payment.id
                            )
                        )

                    log_payment_event(
                        payment,
                        event="status_change",
                        old_status=payment.status,
                        new_status=status,
                        origin="payment_admin_action",
                        user=request.user,
                    )
                    change_payment_status(payment, status)
                    payment.save()
                    notify_status_change(payment)
        except PaymentException as exception:
            modeladmin.message_user(request, exception, level=messages.WARNING)

    # have to change the function name so that django admin see that they are different functions
    action.__name__ = f"change_to_{status}"
    action.short_description = description

    return action


class PaymentManagementAdminMixin:
    @admin.display(description="Statut du paiement")
    def status_buttons(self, payment):
        if not payment or not payment.id:
            return "-"

        if payment.status not in [
            Payment.STATUS_WAITING,
            Payment.STATUS_REFUSED,
            Payment.STATUS_ABANDONED,
        ]:
            return payment.get_status_display()

        if not PAYMENT_MODES[payment.mode].can_admin:
            return format_html(
                '<p>{}</p><p><a href="{}" target="_blank" class="button">Effectuer le paiement en ligne</a>'
                ' <button type="submit" class="button" name="_changestatus" value="{}">Annuler le paiement</button></p>',
                payment.get_status_display(),
                front_url("payment_retry", args=[payment.pk]),
                Payment.STATUS_CANCELED,
            )

        statuses = [
            (Payment.STATUS_COMPLETED, "Valider"),
            (Payment.STATUS_CANCELED, "Annuler"),
        ]

        return format_html(
            "{}<p>{}</p>",
            payment.get_status_display(),
            format_html_join(
                " ",
                '<button type="submit" class="button" name="_changestatus" value="{}">{}</button>',
                ((status, label) for status, label in statuses),
            ),
        )

    @admin.display(description="Mode de paiement")
    def change_mode_buttons(self, payment):
        if not payment or not payment.id:
            return "-"

        if payment.status in (
            Payment.STATUS_COMPLETED,
            Payment.STATUS_CANCELED,
            Payment.STATUS_REFUND,
        ):
            return payment.get_mode_display()

        if (admin_modes := PAYMENT_TYPES[payment.type].admin_modes) is not None:
            if callable(PAYMENT_TYPES[payment.type].admin_modes):
                admin_modes = admin_modes(payment)

            payment_modes = {k: v for k, v in PAYMENT_MODES.items() if k in admin_modes}
        else:
            payment_modes = PAYMENT_MODES

        return format_html_join(
            " ",
            '<button type="submit" class="button" name="_changemode" {} value="{}">{}</button>',
            (
                (
                    "disabled" if payment.mode == id else "",
                    id,
                    f"{mode.label} ({id})",
                )
                for id, mode in payment_modes.items()
            ),
        )

    def save_form(self, request, form, change):
        with transaction.atomic():
            if "_changemode" in request.POST:
                if request.POST["_changemode"] not in PAYMENT_MODES:
                    raise SuspiciousOperation()

                mode = request.POST["_changemode"]
                payment = form.instance
                log_payment_event(
                    payment,
                    event="mode_change",
                    old_mode=payment.mode,
                    new_mode=mode,
                    origin=self.opts.app_label + "_admin_change_mode",
                    user=request.user,
                )

            if "_changestatus" in request.POST:
                if int(request.POST["_changestatus"]) not in [
                    Payment.STATUS_COMPLETED,
                    Payment.STATUS_REFUSED,
                    Payment.STATUS_CANCELED,
                ]:
                    raise SuspiciousOperation()

                status = request.POST["_changestatus"]
                payment = form.instance
                log_payment_event(
                    payment,
                    event="status_change",
                    old_status=payment.status,
                    new_status=status,
                    origin=self.opts.app_label + "_admin_change_button",
                    user=request.user,
                )
                change_payment_status(payment, int(status))
                notify_status_change(payment)

            return super().save_form(request, form, change)

    def response_change(self, request, payment):
        if "_changemode" in request.POST:
            if not PAYMENT_MODES[payment.mode].can_admin:
                return HttpResponseRedirect(payment.get_payment_url())

            self.message_user(
                request, "Le mode de paiement a bien été modifié.", messages.SUCCESS
            )
            return HttpResponseRedirect(request.path)

        if "_changestatus" in request.POST:
            self.message_user(
                request, "Le statut du paiement a bien été modifié.", messages.SUCCESS
            )
            return HttpResponseRedirect(request.path)

        return super().response_change(request, payment)

    def get_urls(self):
        return [
            path(
                "<int:payment_pk>/cancel-or-refund/",
                self.admin_site.admin_view(self.cancel_or_refund_view),
                name="payments_payment_cancel_or_refund",
            )
        ] + super().get_urls()

    @admin.display(description="Remboursement")
    def cancel_or_refund_button(self, payment):
        if payment._state.adding:
            return "-"

        if not payment.can_refund():
            return "Le remboursement n'est pas disponible pour ce paiement"

        return format_html(
            '<a href="{}" class="button">Annuler et rembourser le paiement</a>'
            '<div class="help" style="margin: 0; padding: 4px 0 0;">'
            "&#9888; Si le paiement est lié à la participation à un événement, celle-ci sera également annulée"
            "</div>",
            reverse("admin:payments_payment_cancel_or_refund", args=(payment.pk,)),
        )

    def cancel_or_refund_view(self, request, payment_pk):
        try:
            payment = Payment.objects.get(pk=payment_pk)
        except Payment.DoesNotExist:
            raise Http404()

        if not payment.can_refund():
            self.message_user(
                request,
                "Le remboursement n'est pas disponible pour ce mode de paiement.",
                level=messages.WARNING,
            )
            return redirect("admin:payments_payment_change", payment_pk)

        if request.method == "POST":
            try:
                log_payment_event(
                    payment,
                    event="cancel_or_refund_payment",
                    origin=self.opts.app_label + "_admin_cancel_or_refund_view",
                    user=request.user,
                )
                cancel_or_refund_payment(payment)
            except NotImplementedError:
                self.message_user(
                    request,
                    "Le remboursement n'est pas disponible pour ce mode de paiement.",
                    level=messages.WARNING,
                )
            except (ValueError, SystemPayError) as e:
                self.message_user(
                    request,
                    f"Le remboursement a échoué : {repr(e)}",
                    level=messages.WARNING,
                )
            else:
                self.message_user(
                    request,
                    "Le paiement a bien été annulé et remboursé",
                    level=messages.SUCCESS,
                )

            return redirect("admin:payments_payment_change", payment_pk)

        context = {
            "title": "Annuler et rembourer le paiement : %s" % escape(payment_pk),
            "is_popup": True,
            "opts": self.model._meta,
            "payment": payment,
            "change": True,
            "add": False,
            "save_as": False,
            "show_save": True,
            "has_delete_permission": self.has_delete_permission(request, payment),
            "has_add_permission": self.has_add_permission(request),
            "has_change_permission": self.has_change_permission(request, payment),
            "has_view_permission": self.has_view_permission(request, payment),
            "has_editable_inline_admin_formsets": False,
        }
        context.update(self.admin_site.each_context(request))

        request.current_app = self.admin_site.name

        return TemplateResponse(
            request, "admin/payments/cancel_or_refund_payment.html", context
        )


class PaymentAdminForm(forms.ModelForm):
    price = MoneyField(
        label="Modifier le prix avant le paiement",
        help_text="La modification arbitraire du montant sera enregistrée si vous validez le paiement.",
    )

    type = forms.ChoiceField(
        required=True,
        label="Type de paiement",
        help_text="Ne modifiez cette valeur que si vous savez exactement ce que vous faites.",
        choices=get_payment_choices,
    )


class PaymentChangeList(ChangeList):
    def get_results(self, *args, **kwargs):
        super().get_results(*args, **kwargs)
        self.sum = self.queryset.aggregate(sum=Sum("price"))["sum"] or 0


@admin.register(models.Payment)
class PaymentAdmin(PaymentManagementAdminMixin, AddRelatedLinkMixin, admin.ModelAdmin):
    form = PaymentAdminForm
    list_display = (
        "id",
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
        return display_json_details(obj.meta, "Données de paiement", is_open=True)

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
        "id",
        "person_link",
        "get_price_display",
        "get_allocations_display",
        "type",
        "status",
        "created",
        "mode",
        "day_of_month",
        "end_date",
    )
    readonly_fields = (
        "mode",
        "type",
        "person_link",
        "get_price_display",
        "get_allocations_display",
        "status",
        "terminate_button",
        "end_date",
        "day_of_month",
    )
    fields = readonly_fields
    list_filter = ("status", "mode", ("created", DateRangeFilter))
    search_fields = ("person__search", "=id")

    def get_changelist(self, request, **kwargs):
        return PaymentChangeList

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
