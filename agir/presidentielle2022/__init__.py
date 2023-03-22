from django.conf import settings

from agir.checks import AbstractCheckPaymentMode
from agir.system_pay import AbstractSystemPayPaymentMode, SystemPayConfig


class AFCP2022SystemPayPaymentMode(AbstractSystemPayPaymentMode):
    id = "system_pay_afcp2022"
    url_fragment = "carte-afcp2022"
    title = "Paiement par carte bleue à l'AFCP Mélenchon 2022"
    sp_config = SystemPayConfig(
        site_id=settings.SYSTEMPAY_AFCP2022_SITE_ID,
        production=settings.SYSTEMPAY_AFCP2022_PRODUCTION,
        currency=settings.SYSTEMPAY_CURRENCY,
        certificate=settings.SYSTEMPAY_AFCP2022_CERTIFICATE,
    )


class AFCPJLMCheckEventPaymentMode(AbstractCheckPaymentMode):
    id = "check_jlm2022_evenements"
    url_fragment = "cheque-melenchon2022-evenements"

    order = "AFCP JLM 2022"
    address = ["Mélenchon 2022 — Service Événement", "25 passage Dubail", "75010 Paris"]

    additional_information = (
        "Votre versement ne sera confirmé qu'à réception du chèque. Vous recevrez un message de confirmation quand ce "
        " sera fait."
    )


class AFCPJLMCheckDonationPaymentMode(AbstractCheckPaymentMode):
    id = "check_jlm2022_dons"
    url_fragment = "cheque-melenchon2022-dons"

    order = "AFCP JLM 2022"
    address = ["Mélenchon 2022 — Service Dons", "25 passage Dubail", "75010 Paris"]

    additional_information = (
        "Votre versement ne sera confirmé qu'à réception du chèque. Vous recevrez un message de confirmation quand ce "
        " sera fait."
    )
