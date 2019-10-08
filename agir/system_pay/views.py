import logging
from datetime import date

import calendar
from uuid import UUID

from django.db import transaction
from django.http import (
    HttpResponseForbidden,
    HttpResponseBadRequest,
    HttpResponseNotFound,
    HttpResponse,
)
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.cache import add_never_cache_headers
from django.views.generic import TemplateView
from rest_framework.views import APIView

from agir.authentication.models import Role
from agir.payments.actions.payments import (
    notify_status_change,
    create_payment,
    refund_payment,
)
from agir.payments.actions.subscriptions import (
    notify_status_change as notify_subscription_status_change,
)
from agir.payments.models import Payment, Subscription
from agir.payments.views import handle_return, handle_subscription_return
from agir.system_pay import AbstractSystemPayPaymentMode
from agir.system_pay.actions import (
    update_payment_from_transaction,
    update_subscription_from_transaction,
)
from agir.system_pay.models import SystemPayTransaction, SystemPayAlias
from .crypto import check_signature
from .forms import SystempayPaymentForm, SystempayNewSubscriptionForm

logger = logging.getLogger(__name__)

SYSTEMPAY_STATUS_CHOICE = {
    "ABANDONED": SystemPayTransaction.STATUS_ABANDONED,
    "CANCELED": SystemPayTransaction.STATUS_CANCELED,
    "REFUSED": SystemPayTransaction.STATUS_REFUSED,
    "AUTHORISED": SystemPayTransaction.STATUS_COMPLETED,
    "AUTHORISED_TO_VALIDATE": SystemPayTransaction.STATUS_COMPLETED,
    "ACCEPTED": SystemPayTransaction.STATUS_COMPLETED,
    "CAPTURED": SystemPayTransaction.STATUS_COMPLETED,
}
SYSTEMPAY_OPERATION_TYPE_CHOICE = ["DEBIT", "CREDIT", "VERIFICATION"]
PAYMENT_ID_SESSION_KEY = "_payment_id"
SUBSCRIPTION_ID_SESSION_KEY = "_payment_id"


class BaseSystemPayRedirectView(TemplateView):
    template_name = "system_pay/redirect.html"
    sp_config = None


class SystempayRedirectView(BaseSystemPayRedirectView):
    def get_context_data(self, **kwargs):
        return super().get_context_data(
            form=SystempayPaymentForm.get_form_for_transaction(
                self.transaction, self.sp_config
            ),
            **kwargs
        )

    def get(self, request, *args, **kwargs):
        self.payment = kwargs["payment"]
        self.transaction = SystemPayTransaction.objects.create(payment=self.payment)
        res = super().get(request, *args, **kwargs)
        add_never_cache_headers(res)

        # save payment in session
        request.session[PAYMENT_ID_SESSION_KEY] = self.payment.pk

        return res


class SystemPaySubscriptionRedirectView(BaseSystemPayRedirectView):
    def get_context_data(self, **kwargs):
        return super().get_context_data(
            form=SystempayNewSubscriptionForm.get_form_for_transaction(
                self.transaction, self.sp_config
            ),
            **kwargs
        )

    def get(self, request, *args, **kwargs):
        self.subscription = kwargs["subscription"]
        self.transaction = SystemPayTransaction.objects.create(
            subscription=self.subscription
        )
        res = super().get(request, *args, **kwargs)

        # save payment in session
        request.session[SUBSCRIPTION_ID_SESSION_KEY] = self.subscription.pk

        return res


class SystemPayWebhookView(APIView):
    permission_classes = []
    sp_config = None
    mode_id = None

    def post(self, request):
        if (
            request.data.get("vads_trans_status") not in SYSTEMPAY_STATUS_CHOICE
            or request.data.get("vads_operation_type")
            not in SYSTEMPAY_OPERATION_TYPE_CHOICE
            or "vads_order_id" not in request.data
            or "signature" not in request.data
        ):
            logger.exception("Requête malformée de Systempay")
            return HttpResponseBadRequest()
        if not check_signature(request.data, self.sp_config["certificate"]):
            return HttpResponseForbidden()

        with transaction.atomic():
            try:
                # En cas paiement automatique, c'est l'id de la transaction de souscription d'origine qui est indiquée
                # dans vads_order_id, en cas de remboursement, c'est la transaction de paiement d'origine
                sp_transaction = SystemPayTransaction.objects.get(
                    pk=request.data["vads_order_id"]
                )
            except SystemPayTransaction.DoesNotExist:
                return HttpResponseNotFound()

            if (
                "vads_trans_id" in request.data
                and str(int(request.data["vads_order_id"]) % 900000).zfill(6)
                != request.data["vads_trans_id"]
            ):
                is_refund = request.data["vads_operation_type"] == "CREDIT"
                # Il s'agit d'une transaction déclenchée côté Systempay : soit un remboursement, soit un paiement d'un
                # abonnement
                if is_refund:  # c'est un remboursement
                    assert sp_transaction.payment.person.id == UUID(
                        request.data["vads_cust_id"]
                    )
                    assert sp_transaction.payment.price == int(
                        request.data["vads_amount"]
                    )
                else:  # c'est une subscription
                    # Dans ce cas, l'appel du webhook est en lien à un paiement automatique
                    # sp_transaction pointe pour l'instant vers la transaction de souscription, donc on crée une nouvelle
                    # transaction
                    assert sp_transaction.subscription.person.id == UUID(
                        request.data["vads_cust_id"]
                    )
                    assert sp_transaction.subscription.price == int(
                        request.data["vads_amount"]
                    )

                try:
                    # On s'assure de l'idempotence du webhook en vérifiant toutefois si la nouvelle transaction
                    # n'a pas été créée
                    sp_transaction = SystemPayTransaction.objects.get(
                        uuid=request.data["vads_trans_uuid"]
                    )
                except SystemPayTransaction.DoesNotExist:
                    if is_refund:  # c'est un remboursement
                        payment = sp_transaction.payment
                    else:  # c'est une souscription
                        payment = create_payment(
                            person=sp_transaction.subscription.person,
                            type=sp_transaction.subscription.type,
                            price=request.data["vads_amount"],
                            mode=self.mode_id,
                            subscription=sp_transaction.subscription,
                        )
                    # la transaction a été crée par systempay et non par formulaire, elle n'existe pas côté plateforme
                    sp_transaction = SystemPayTransaction.objects.create(
                        payment=payment, is_refund=is_refund
                    )

            if "vads_identifier" in request.data:
                # en cas d'alias, il s'agit soit d'une transaction de souscription, soit d'un paiement automatique
                expiry_year = int(request.data["vads_expiry_year"])
                expiry_month = int(request.data["vads_expiry_month"])
                alias, is_new = SystemPayAlias.objects.get_or_create(
                    identifier=request.data["vads_identifier"],
                    defaults={
                        "expiry_date": date(
                            year=expiry_year,
                            month=expiry_month,
                            day=calendar.monthrange(expiry_year, expiry_month)[1],
                        )
                    },
                )
                sp_transaction.alias = alias

            sp_transaction.webhook_calls.append(request.data)
            sp_transaction.status = SYSTEMPAY_STATUS_CHOICE.get(
                request.data["vads_trans_status"]
            )
            sp_transaction.uuid = request.data.get("vads_trans_uuid")
            sp_transaction.save()

            if sp_transaction.payment is not None:
                update_payment_from_transaction(sp_transaction.payment, sp_transaction)
            elif sp_transaction.subscription is not None:
                update_subscription_from_transaction(
                    sp_transaction.subscription, sp_transaction
                )
            else:
                logger.exception("Transaction Systempay sans paiement ni abonnement.")
                return HttpResponseNotFound()

        if sp_transaction.payment is not None:
            with transaction.atomic():
                notify_status_change(sp_transaction.payment)

        if sp_transaction.subscription is not None:
            with transaction.atomic():
                notify_subscription_status_change(sp_transaction.subscription)

        return HttpResponse({"status": "Accepted"}, 200)


def return_view(request):
    payment_id = request.session.get(PAYMENT_ID_SESSION_KEY)
    payment = None
    subscription_id = request.session.get(SUBSCRIPTION_ID_SESSION_KEY)
    subscription = None

    status = request.GET.get("status")

    if payment_id or subscription:
        try:
            payment = Payment.objects.get(pk=payment_id)
        except Payment.DoesNotExist:
            pass

    if subscription_id:
        try:
            subscription = Subscription.objects.get(pk=subscription_id)
        except Subscription.DoesNotExist:
            pass

    if (
        payment is None
        and subscription is None
        and request.user.is_authenticated
        and request.user.type == Role.PERSON_ROLE
    ):
        try:
            system_pay_modes = [
                klass.id for klass in AbstractSystemPayPaymentMode.__subclasses__()
            ]
            two_hours_ago = timezone.now() - timezone.timedelta(hours=2)
            payment = (
                request.user.person.payments.filter(
                    mode__in=system_pay_modes, created__gt=two_hours_ago
                )
                .order_by("-created")
                .first()
            )
        except Payment.DoesNotExist:
            pass

    if status != "success":
        return TemplateResponse(request, "system_pay/payment_failed.html")

    if payment is None and subscription is None:
        return TemplateResponse(request, "system_pay/payment_not_identified.html")

    if payment is not None:
        return handle_return(request, payment)

    if subscription is not None:
        return handle_subscription_return(request, subscription)
