from django.conf.urls import url
from django.urls import reverse_lazy
from django.views.generic import TemplateView, RedirectView

from .views import SystempayRedirectView, SystempayWebhookView, success_view, failure_view

urlpatterns = [
    url('^paiement/systempay_webhook/$', SystempayWebhookView.as_view(), name='systempay_webhook'),
    url('^paiement/(?P<pk>[0-9]+)/$', SystempayRedirectView.as_view(), name='payment_redirect'),
    url('^paiement/success/$', success_view, name='payment_success'),
    url('^paiement/echec/$', failure_view, name='payment_failure'),
    url('^paiement/retour/$', RedirectView.as_view(url=reverse_lazy('payment_success')))
]
