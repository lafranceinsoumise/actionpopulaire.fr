from agir.api import settings
from agir.system_pay import AbstractSystemPayPaymentMode

default_app_config = "agir.donations.apps.DonsConfig"


class AFCP2022SystemPayPaymentMode(AbstractSystemPayPaymentMode):
    id = "system_pay_afcp2022"
    url_fragment = "carte-afcp2022"
    label = (
        "Paiement par carte bleue à l'AFCP Mélenchon 2022 (Association de financement de la campagne "
        "présidentielle Mélenchon 2022) "
    )
    sp_config = {
        "site_id": settings.SYSTEMPAY_AFCP2022_SITE_ID,
        "production": settings.SYSTEMPAY_AFCP2022_PRODUCTION,
        "currency": settings.SYSTEMPAY_CURRENCY,
        "certificate": settings.SYSTEMPAY_AFCP2022_CERTIFICATE,
    }
