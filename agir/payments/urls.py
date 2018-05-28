from django.urls import path
from django.urls import reverse_lazy
from django.views.generic import RedirectView

from .views import SystempayRedirectView, SystempayWebhookView, success_view, failure_view

urlpatterns = [
    path('paiement/systempay_webhook/', SystempayWebhookView.as_view(), name='systempay_webhook'),
    path('paiement/<int:pk>/', SystempayRedirectView.as_view(), name='payment_redirect'),
    path('paiement/success/', success_view, name='payment_success'),
    path('paiement/echec/', failure_view, name='payment_failure'),
    path('paiement/retour/', RedirectView.as_view(url=reverse_lazy('payment_success')))
]
