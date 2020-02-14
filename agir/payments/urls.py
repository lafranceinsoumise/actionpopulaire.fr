from django.urls import path, include

from .payment_modes import PAYMENT_MODES
from .views import (
    PaymentView,
    RetryPaymentView,
    payment_return_view,
    SubscriptionView,
    TerminateSubscriptionView,
    subscription_return_view,
)

urlpatterns = [
    path("paiement/<int:pk>/", PaymentView.as_view(), name="payment_page"),
    path(
        "paiement/<int:pk>/reessayer/", RetryPaymentView.as_view(), name="payment_retry"
    ),
    path("paiement/<int:pk>/retour/", payment_return_view, name="payment_return"),
    path("abonnement/<int:pk>", SubscriptionView.as_view(), name="subscription_page"),
    path(
        "abonnement/<int:pk>/retour/",
        subscription_return_view,
        name="subscription_return",
    ),
    path(
        "abonnement/<int:pk>/annuler",
        TerminateSubscriptionView.as_view(),
        name="subscription_terminate",
    ),
]
