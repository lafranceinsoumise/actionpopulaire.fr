from django.urls import path, include

from .payment_modes import PAYMENT_MODES
from .views import PaymentView, RetryPaymentView, return_view

urlpatterns = [
    path('paiement/<int:pk>/', PaymentView.as_view(), name='payment_page'),
    path('paiement/<int:pk>/reessayer/', RetryPaymentView.as_view(), name='payment_retry'),
    path('paiement/<int:pk>/retour/', return_view, name='payment_return')
]

for payment_mode in PAYMENT_MODES.values():
    urlpatterns.append(
        path(f'paiement/{payment_mode.url_fragment}/', include((payment_mode.get_urls(), payment_mode.id)))
    )
