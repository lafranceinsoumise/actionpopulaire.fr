from django.utils.translation import ugettext_lazy as _

from agir.checks.payment_mode import AbstractCheckPaymentMode


class CheckPaymentMode(AbstractCheckPaymentMode):
    id = "check"
    url_fragment = "cheque"
    label = _("Paiement par chèque")

    order = "AFLFI"
    address = ["AFLFI - Service événements", "43 rue de Dunkerque", "75010 Paris"]
    additional_information = (
        "Votre participation ne sera confirmée qu'à réception du chèque. Vous recevrez un message de confirmation"
        " quand ce sera fait (à moins que vous n'ayez désactivé les notifications d'événement)."
    )

    warnings = [
        "N'oubliez pas d'indiquer le numéro de commande au dos de votre chèque",
        "Votre chèque doit être envoyé par la poste : aucune remise du chèque au moment de l'événement n'est"
        "généralement possible, et votre participation ne sera pas garantie si vous ne tenez pas compte de cette"
        "consigne.",
    ]
