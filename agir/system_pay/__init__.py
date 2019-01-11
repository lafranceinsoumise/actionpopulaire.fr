from django.conf import settings
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

    webhook_url = "webhook/"
    return_url = "retour/"
    sp_config = {
        "site_id": settings.SYSTEMPAY_SITE_ID,
        "production": settings.SYSTEMPAY_PRODUCTION,
        "currency": settings.SYSTEMPAY_CURRENCY,
        "certificate": settings.SYSTEMPAY_CERTIFICATE,
    }

    @cached_property
    def payment_view(self):
        from . import views

        return views.SystempayRedirectView.as_view(sp_config=self.sp_config)

    @cached_property
    def retry_payment_view(self):
        from . import views

        return views.SystempayRedirectView.as_view(sp_config=self.sp_config)

    @classmethod
    def get_urls(cls):
        from . import views

        return [
            path(
                cls.webhook_url,
                views.SystemPayWebhookView.as_view(sp_config=cls.sp_config),
                name="webhook",
            ),
            path(cls.return_url, views.return_view, name="return"),
        ]
