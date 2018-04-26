import hmac
from django.conf import settings
from django.db.models.expressions import F
from django.http import (
    HttpResponseRedirect, HttpResponseForbidden, HttpResponseBadRequest, HttpResponseNotFound, HttpResponse
)
from django.urls import reverse
from django.views.generic import DetailView, TemplateView
from django.shortcuts import resolve_url
from rest_framework.views import APIView

from .forms import get_signature
from .models import Payment
from .types import PAYMENT_TYPES


PAYMENT_ID_SESSION_KEY = '_payment_id'


class SystempayRedirectView(DetailView):
    context_object_name = 'payment'
    template_name = 'payments/redirect.html'
    queryset = Payment.objects.filter(status=Payment.STATUS_WAITING)

    def get(self, request, *args, **kwargs):
        res = super().get(request, *args, **kwargs)
        request.session[PAYMENT_ID_SESSION_KEY] = self.object.pk
        return res


class SystempayWebhookView(APIView):
    permission_classes = []

    SYSTEMPAY_STATUS_CHOICE = {
        'ABANDONED': Payment.STATUS_ABANDONED,
        'CANCELED': Payment.STATUS_CANCELED,
        'REFUSED': Payment.STATUS_REFUSED,
        'AUTHORISED': Payment.STATUS_COMPLETED,
        'AUTHORISED_TO_VALIDATE': Payment.STATUS_COMPLETED,
    }

    def post(self, request):
        print(get_signature(request.data) + ' lol')

        if not hmac.compare_digest(get_signature(request.data), request.data['signature']):
            return HttpResponseForbidden()

        if request.data.get('vads_trans_status') not in self.SYSTEMPAY_STATUS_CHOICE or not request.data.get('vads_trans_id'):
            return HttpResponseBadRequest()

        payment = Payment.objects.annotate(systempay_id=F('id') % 900000).filter(systempay_id=request.data['vads_trans_id']).last()
        if payment is None:
            return HttpResponseNotFound()

        payment.systempay_responses.append(request.data)
        payment.status = self.SYSTEMPAY_STATUS_CHOICE.get(request.data['vads_trans_status'])
        payment.save()

        return HttpResponse({'status': 'Accepted'}, 200)


def success_view(request):
    pk = request.session.get(PAYMENT_ID_SESSION_KEY)

    if pk is not None:
        try:
            payment = Payment.objects.get(pk=pk)
            if payment.type in PAYMENT_TYPES and PAYMENT_TYPES[payment.type].success_view:
                return PAYMENT_TYPES[payment.type].success_view(request, payment=payment)
        except Payment.DoesNotExist:
            pass

    return TemplateView.as_view(template_name='payments/success.html')(request)


def failure_view(request):
    pk = request.session.get(PAYMENT_ID_SESSION_KEY)

    if pk is not None:
        try:
            payment = Payment.objects.get(pk=pk)
            if payment.type in PAYMENT_TYPES and PAYMENT_TYPES[payment.type].failure_view:
                return PAYMENT_TYPES[payment.type].failure_view(request, payment=payment)
        except Payment.DoesNotExist:
            pass

    return TemplateView.as_view(template_name='payments/failure.html')(request)
