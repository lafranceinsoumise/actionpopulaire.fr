from django.conf import settings

from agir.system_pay import SystemPayConfig, AbstractSystemPayPaymentMode


class Europeennes2024PretsPaymentMode(AbstractSystemPayPaymentMode):
    id = "systempay_prets_europeennes2024"
    url_fragment = "prets-afcp2024"
    title = "Prêt par carte bleue à l'AFCP pour les Européennes 2024"
    sp_config = SystemPayConfig(
        site_id=settings.SYSTEMPAY_AFCP2024_PRETS_SITE_ID,
        production=settings.SYSTEMPAY_AFCP2024_PRETS_PRODUCTION,
        certificate=settings.SYSTEMPAY_AFCP2024_PRETS_CERTIFICATE,
        currency=settings.SYSTEMPAY_CURRENCY,
    )


class Europeennes2024DonsPaymentMode(AbstractSystemPayPaymentMode):
    id = "systempay_dons_europeennes2024"
    url_fragment = "dons-afcp2024"
    title = "Dons par carte bleue à l'AFCP pour les européennes 2024"
    sp_config = SystemPayConfig(
        site_id=settings.SYSTEMPAY_AFCP2024_DONS_SITE_ID,
        production=settings.SYSTEMPAY_AFCP2024_DONS_PRODUCTION,
        certificate=settings.SYSTEMPAY_AFCP2024_DONS_CERTIFICATE,
        currency=settings.SYSTEMPAY_CURRENCY,
    )
