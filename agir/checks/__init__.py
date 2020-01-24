from django.utils.translation import ugettext_lazy as _

from agir.checks.payment_mode import AbstractCheckPaymentMode


class CheckPaymentMode(AbstractCheckPaymentMode):
    id = "check"
    url_fragment = "cheque"
    label = _("Par chèque")

    order = "AFLFI"
    address = ["AFLFI", "43 rue de Dunkerque", "75010 Paris"]
    additional_information = (
        "Votre versement ne sera confirmée qu'à réception du chèque. Vous recevrez un message de confirmation"
        " quand ce sera fait (à moins que vous n'ayez désactivé les notifications)."
    )

    warnings = [
        "N'oubliez pas d'indiquer le numéro au dos de votre chèque ! Seul celui-ci permettra de traiter votre chèque dans les meilleurs délais."
    ]
