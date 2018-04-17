import hmac
from django.db.models.expressions import F
from django.http import HttpResponseForbidden, HttpResponseBadRequest, HttpResponseNotFound, HttpResponse
from django.views.generic import DetailView
from rest_framework.views import APIView

from payments.forms import get_signature
from payments.models import Payment


class SystempayRedirectView(DetailView):
    context_object_name = 'payment'
    template_name = 'payments/redirect.html'

    def get_queryset(self):
        return Payment.objects.filter(status=Payment.STATUS_WAITING)


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
