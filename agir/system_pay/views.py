from django.db import transaction
from django.http import HttpResponseForbidden, HttpResponseBadRequest, HttpResponseNotFound, HttpResponse
from django.template.response import TemplateResponse
from django.views.generic import TemplateView
from rest_framework.views import APIView

from agir.payments.actions import notify_status_change
from agir.payments.models import Payment
from agir.payments.views import handle_return
from agir.system_pay.actions import update_payment_from_transaction
from agir.system_pay.models import SystemPayTransaction

from .crypto import check_signature
from .forms import SystempayRedirectForm


SYSTEMPAY_STATUS_CHOICE = {
    'ABANDONED': SystemPayTransaction.STATUS_ABANDONED,
    'CANCELED': SystemPayTransaction.STATUS_CANCELED,
    'REFUSED': SystemPayTransaction.STATUS_REFUSED,
    'AUTHORISED': SystemPayTransaction.STATUS_COMPLETED,
    'AUTHORISED_TO_VALIDATE': SystemPayTransaction.STATUS_COMPLETED,
}
PAYMENT_ID_SESSION_KEY = '_payment_id'


class SystempayRedirectView(TemplateView):
    template_name = 'system_pay/redirect.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            form=SystempayRedirectForm.get_form_for_transaction(self.transaction),
            **kwargs
        )

    def get(self, request, *args, **kwargs):
        self.payment = kwargs['payment']
        self.transaction = SystemPayTransaction.objects.create(payment=self.payment)
        res = super().get(request, *args, **kwargs)

        # save payment in session
        request.session[PAYMENT_ID_SESSION_KEY] = self.payment.pk

        return res


class SystemPayWebhookView(APIView):
    permission_classes = []

    def post(self, request, ):
        if not check_signature(request.data):
            return HttpResponseForbidden()

        if request.data.get('vads_trans_status') not in SYSTEMPAY_STATUS_CHOICE or not request.data.get(
                'vads_order_id'):
            return HttpResponseBadRequest()

        try:
            sp_transaction = SystemPayTransaction.objects.get(pk=request.data['vads_order_id'])
        except SystemPayTransaction.DoesNotExist:
            return HttpResponseNotFound()

        with transaction.atomic():
            sp_transaction.webhook_calls.append(request.data)
            sp_transaction.status = SYSTEMPAY_STATUS_CHOICE.get(request.data['vads_trans_status'])
            sp_transaction.save()

            update_payment_from_transaction(sp_transaction.payment, sp_transaction)

        with transaction.atomic():
            notify_status_change(sp_transaction.payment)

        return HttpResponse({'status': 'Accepted'}, 200)


def return_view(request):
    payment_id = request.session.get(PAYMENT_ID_SESSION_KEY)
    payment = None

    status = request.GET.get('status')

    if payment_id:
        try:
            payment = Payment.objects.get(pk=payment_id)
        except Payment.DoesNotExist:
            pass

    if payment is None:
        return TemplateResponse(
            request, 'system_pay/payment_not_identified.html'
        )

    if status != 'success':
        return TemplateResponse(
            request, 'system_pay/payment_failed.html'
        )

    return handle_return(request, payment)
