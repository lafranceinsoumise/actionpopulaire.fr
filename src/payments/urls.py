from django.conf.urls import url

from payments.views import SystempayRedirectView, SystempayWebhookView

urlpatterns = [
    url('^payment/systempay_webhook/$', SystempayWebhookView.as_view(), name='payment_redirect'),
    url('^payment/(?P<pk>[0-9]+)/$', SystempayRedirectView.as_view(), name='payment_redirect'),
]
