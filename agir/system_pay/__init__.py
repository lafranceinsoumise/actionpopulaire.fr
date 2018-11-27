from django.urls import path
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property

from ..payments.abstract_payment_mode import AbstractPaymentMode


class SystemPayPaymentMode(AbstractPaymentMode):
    id = "system_pay"
    url_fragment = "carte"
    label = _("Paiement par carte bleue")

    can_retry = True
    can_cancel = True

    @cached_property
    def payment_view(self):
        from . import views

        return views.SystempayRedirectView.as_view()

    @cached_property
    def retry_payment_view(self):
        from . import views

        return views.SystempayRedirectView.as_view()

    @staticmethod
    def get_urls():
        from . import views

        return [
            path("webhook/", views.SystemPayWebhookView.as_view(), name="webhook"),
            path("retour/", views.return_view, name="return"),
        ]
