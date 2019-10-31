from django.conf import settings
from django.urls import path
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from ..payments.abstract_payment_mode import AbstractPaymentMode


class AbstractSystemPayPaymentMode(AbstractPaymentMode):
    can_retry = True
    can_cancel = True

    webhook_url = "webhook/"
    return_url = "retour/"

    id = None
    url_fragment = None
    label = None
    category = "payment_card"

    sp_config = {
        "site_id": None,
        "production": None,
        "currency": None,
        "certificate": None,
    }

    @cached_property
    def soap_client(self):
        from agir.system_pay.soap_client import SystemPaySoapClient

        return SystemPaySoapClient(self.sp_config)

    @cached_property
    def payment_view(self):
        from . import views

        return views.SystempayRedirectView.as_view(sp_config=self.sp_config)

    @cached_property
    def retry_payment_view(self):
        from . import views

        return views.SystempayRedirectView.as_view(sp_config=self.sp_config)

    @cached_property
    def subscription_view(self):
        from . import views

        return views.SystemPaySubscriptionRedirectView.as_view(sp_config=self.sp_config)

    def subscription_terminate_action(self, subscription):
        sp_subscription = subscription.system_pay_subscription
        alias = sp_subscription.alias
        self.soap_client.cancel_subscription(subscription.system_pay_subscription.alias)
        alias.active = False
        alias.save(update_fields=["active"])
        sp_subscription.active = False
        sp_subscription.save(update_fields=["active"])

    @classmethod
    def get_urls(cls):
        from . import views

        return [
            path(
                cls.webhook_url,
                views.SystemPayWebhookView.as_view(
                    sp_config=cls.sp_config, mode_id=cls.id
                ),
                name="webhook",
            ),
            path(cls.return_url, views.return_view, name="return"),
        ]


class SystemPayPaymentMode(AbstractSystemPayPaymentMode):
    id = "system_pay"
    url_fragment = "carte"
    label = _("Paiement par carte bleue")

    sp_config = {
        "site_id": settings.SYSTEMPAY_SITE_ID,
        "production": settings.SYSTEMPAY_PRODUCTION,
        "currency": settings.SYSTEMPAY_CURRENCY,
        "certificate": settings.SYSTEMPAY_CERTIFICATE,
    }


class SystemPayError(Exception):
    def __init__(self, message, system_pay_code=None):
        super().__init__(message, system_pay_code)
        self.message = message
        self.system_pay_code = system_pay_code

    def __str__(self):
        return self.message

    def __repr__(self):
        return f"SystemPayError({self.message!r}, system_pay_code={self.system_pay_code!r})"
