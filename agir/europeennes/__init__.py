from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from agir.checks import AbstractCheckPaymentMode
from agir.system_pay import SystemPayPaymentMode

default_app_config = "agir.europeennes.apps.EuropeennesConfig"


class AFCESystemPayPaymentMode(SystemPayPaymentMode):
    id = "system_pay_afce"
    url_fragment = "carte-afce"
    label = _(
        "Paiement par carte bleue à l'AFCE LFI 2019 (Association de financement de la campagne européenne de la France insoumise)"
    )

    sp_config = {
        "site_id": settings.SYSTEMPAY_AFCE_SITE_ID,
        "production": settings.SYSTEMPAY_AFCE_PRODUCTION,
        "currency": settings.SYSTEMPAY_CURRENCY,
        "certificate": settings.SYSTEMPAY_AFCE_CERTIFICATE,
    }


class AFCELoansSystemPayPaymentMode(SystemPayPaymentMode):
    id = "system_pay_afce_pret"
    url_fragment = "carte-afce-pret"
    label = _("Versement par carte bleue à l'AFCE LFI 2019")

    sp_config = {
        "site_id": settings.SYSTEMPAY_AFCE_LOANS_SITE_ID,
        "production": settings.SYSTEMPAY_AFCE_LOANS_PRODUCTION,
        "currency": settings.SYSTEMPAY_CURRENCY,
        "certificate": settings.SYSTEMPAY_AFCE_LOANS_CERTIFICATE,
    }


class AFCECheckPaymentMode(AbstractCheckPaymentMode):
    id = "check_afce"
    url_fragment = "afce_cheque"
    label = _("Chèque à l'ordre de l'AFCE LFI 2019")

    title = "Votre versement par chèque"
    order = "AFCE LFI 2019"
    address = ["AFCE LFI 2019", "43 rue de Dunkerque", "75010 Paris"]
    additional_information = (
        "Votre prêt ne sera confirmé qu'à réception du chèque. Vous recevrez un email contenant le contrat signé dès"
        " que votre chèque aura été traité."
    )
    warnings = [
        "N'oubliez pas d'indiquer le numéro de transaction au dos de votre chèque pour faciliter son traitement !",
        "Vous ne recevrez le contrat signé qu'une fois votre chèque reçu.",
    ]
