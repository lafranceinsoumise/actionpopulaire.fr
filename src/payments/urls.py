from django.conf.urls import url

from payments.views import SystempayRedirectView, SystempayWebhookView, return_view

urlpatterns = [
    url('^paiement/systempay_webhook/$', SystempayWebhookView.as_view(), name='systempay_webhook'),
    url('^paiement/(?P<pk>[0-9]+)/$', SystempayRedirectView.as_view(), name='payment_redirect'),
    url('^paiement/retour/$', return_view, name='payment_return')
]
