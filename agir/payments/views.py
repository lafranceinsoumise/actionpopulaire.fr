from django.contrib import messages
from django.http import Http404, HttpResponseServerError
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.views.generic import DetailView

from agir.authentication.view_mixins import HardLoginRequiredMixin
from agir.payments.actions.subscriptions import terminate_subscription
from .models import Payment, Subscription
from .types import PAYMENT_TYPES, SUBSCRIPTION_TYPES
from .payment_modes import PAYMENT_MODES


PAYMENT_ID_SESSION_KEY = "_payment_id"


def payment_view(request,):
    pass


class PaymentView(DetailView):
    queryset = Payment.objects.filter(status=Payment.STATUS_WAITING)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        payment_mode = PAYMENT_MODES.get(self.object.mode)

        if payment_mode is None:
            return HttpResponseServerError()

        return payment_mode.payment_view(request, payment=self.object, *args, **kwargs)


class RetryPaymentView(DetailView):
    def get_queryset(self):
        return Payment.objects.exclude(status=Payment.STATUS_COMPLETED).filter(
            mode__in=[mode.id for mode in PAYMENT_MODES.values() if mode.can_retry]
        )

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        payment_mode = PAYMENT_MODES.get(self.object.mode)

        if payment_mode is None:
            return HttpResponseServerError()

        return payment_mode.retry_payment_view(
            request, payment=self.object, *args, **kwargs
        )


class SubscriptionView(DetailView):
    queryset = Subscription.objects.filter(status=Subscription.STATUS_WAITING)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        payment_mode = PAYMENT_MODES.get(self.object.mode)

        if payment_mode is None:
            return HttpResponseServerError()

        return payment_mode.subscription_view(
            request, subscription=self.object, *args, **kwargs
        )


class TerminateSubscriptionView(DetailView, HardLoginRequiredMixin):
    template_name = "payments/subscription_terminate.html"

    def get_queryset(self):
        return Subscription.objects.filter(
            status=Subscription.STATUS_COMPLETED, person=self.request.user.person
        )

    def post(self, request, pk):
        subscription = self.get_object()
        terminate_subscription(subscription)

        messages.add_message(
            self.request,
            messages.SUCCESS,
            "Votre paiement automatique a bien été supprimé.",
        )

        return redirect("view_payments")


def return_view(request, pk):
    try:
        payment = Payment.objects.get(pk=pk)
    except Payment.DoesNotExist:
        raise Http404("Ce paiement n'existe pas")

    return handle_return(request, payment)


def handle_return(request, payment):
    if payment.type in PAYMENT_TYPES and PAYMENT_TYPES[payment.type].success_view:
        return PAYMENT_TYPES[payment.type].success_view(request, payment=payment)
    else:
        return TemplateResponse(
            request,
            "payments/success.html"
            if payment.status == payment.STATUS_COMPLETED
            else "payments/failure.html",
        )


def handle_subscription_return(request, subscription):
    if subscription.type in SUBSCRIPTION_TYPES:
        return SUBSCRIPTION_TYPES[subscription.type].success_view(
            request, subscription=subscription
        )
