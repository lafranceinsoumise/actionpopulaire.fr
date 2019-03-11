from django.conf import settings
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from agir.payments.abstract_payment_mode import AbstractPaymentMode
from agir.system_pay import SystemPayPaymentMode


default_app_config = "agir.europeennes.apps.EuropeennesConfig"


class AFCESystemPayPaymentMode(SystemPayPaymentMode):
    id = "system_pay_afce"
    url_fragment = "carte-afce"
    label = _(
        "Paiement par carte bleue à l'AFCE LFI (Association de financement de la campagne européenne de la France insoumise)"
    )

    sp_config = {
        "site_id": settings.SYSTEMPAY_AFCE_SITE_ID,
        "production": settings.SYSTEMPAY_AFCE_PRODUCTION,
        "currency": settings.SYSTEMPAY_CURRENCY,
        "certificate": settings.SYSTEMPAY_AFCE_CERTIFICATE,
    }


class AFCECheckPaymentMode(AbstractPaymentMode):
    id = "check_afce"
    url_fragment = "afce_cheque"
    label = _(
        "Chèque à l'ordre de l'AFCFE LFI (Association de financement de la campagne européenne de la France insoumise)"
    )

    can_retry = True
    can_cancel = True
    can_admin = True

    @cached_property
    def payment_view(self):
        from . import views

        return views.AFCECheckView.as_view()

    @cached_property
    def retry_payment_view(self):
        from . import views

        return views.AFCECheckView.as_view()
