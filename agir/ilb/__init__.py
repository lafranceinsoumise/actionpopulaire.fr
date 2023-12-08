from django.conf import settings

from agir.checks import AbstractCheckPaymentMode
from agir.system_pay import AbstractSystemPayPaymentMode, SystemPayConfig


class ILBSystemPayPaymentMode(AbstractSystemPayPaymentMode):
    id = "system_pay_ilb"
    url_fragment = "carte-ilb"
    title = "Paiement par carte bleue à l'Institut La Boétie"
    sp_config = SystemPayConfig(
        site_id=settings.ILB_SYSTEMPAY_SITE_ID,
        production=settings.ILB_SYSTEMPAY_PRODUCTION,
        currency=settings.ILB_SYSTEMPAY_CURRENCY,
        certificate=settings.ILB_SYSTEMPAY_CERTIFICATE,
        api_password=settings.ILB_SYSTEMPAY_API_PASSWORD,
    )


class ILBCheckPaymentMode(AbstractCheckPaymentMode):
    id = "check_ilb"
    url_fragment = "cheque-ilb"
    order = "Institut La Boétie"
    address = ["Institut la Boétie", "25 passage Dubail", "75010 Paris"]

    additional_information = (
        "Votre versement sera confirmé à réception du chèque, et vous recevrez un email de "
        "confirmation."
    )
