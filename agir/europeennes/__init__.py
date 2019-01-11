from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from agir.system_pay import SystemPayPaymentMode


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
