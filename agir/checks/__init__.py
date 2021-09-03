from django.utils.translation import ugettext_lazy as _

from agir.checks.payment_mode import AbstractCheckPaymentMode


class DonationCheckPaymentMode(AbstractCheckPaymentMode):
    id = "check_donations"
    url_fragment = "cheque-don"
    label = _("Par chèque")

    order = "AFLFI"
    address = ["AFLFI - Dons", "BP 45", "91305 MASSY CEDEX"]
    additional_information = (
        "Votre versement ne sera confirmée qu'à réception du chèque. Vous recevrez un message de confirmation"
        " quand ce sera fait (à moins que vous n'ayez désactivé les notifications)."
    )

    warnings = [
        "N'oubliez pas d'indiquer le numéro au dos de votre chèque ! Seul celui-ci permettra de traiter votre chèque dans les meilleurs délais."
    ]


class EventCheckPaymentMode(AbstractCheckPaymentMode):
    id = "check_events"
    url_fragment = "cheque-evenement"
    label = _("Par chèque")

    order = "AFLFI"
    address = [
        "La France insoumise - Service Événement",
        "25 passage Dubail",
        "75010 Paris",
    ]
    additional_information = (
        "Votre versement ne sera confirmée qu'à réception du chèque. Vous recevrez un message de confirmation"
        " quand ce sera fait (à moins que vous n'ayez désactivé les notifications)."
    )

    warnings = [
        "N'oubliez pas d'indiquer le numéro au dos de votre chèque ! Seul celui-ci permettra de traiter votre chèque dans les meilleurs délais."
    ]
