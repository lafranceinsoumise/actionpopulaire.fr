from django.contrib import admin, messages
from django.core.exceptions import SuspiciousOperation
from django.db import transaction
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse, path
from django.utils.html import escape, format_html, format_html_join

from agir.lib.utils import front_url
from agir.payments.actions.payments import (
    change_payment_status,
    cancel_or_refund_payment,
    log_payment_event,
)
from agir.payments.models import Payment
from agir.payments.payment_modes import PAYMENT_MODES
from agir.payments.types import PAYMENT_TYPES
from agir.system_pay import SystemPayError


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
                payment.mode = mode

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
