from agir.checks.payment_mode import AbstractCheckPaymentMode


class DonationCheckPaymentMode(AbstractCheckPaymentMode):
    id = "check_donations"
    url_fragment = "cheque-don"

    order = "AFLFI"
    address = ["AFLFI - Dons", "BP 45", "91305 MASSY CEDEX"]
    additional_information = (
        "Votre versement ne sera confirmée qu'à réception du chèque. Vous recevrez un message de confirmation"
        " quand ce sera fait (à moins que vous n'ayez désactivé les notifications)."
    )


class EventCheckPaymentMode(AbstractCheckPaymentMode):
    id = "check_events"
    url_fragment = "cheque-evenement"

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


class AFCPJLMCheckPaymentMode(AbstractCheckPaymentMode):
    id = "check_jlm2022_evenements"
    url_fragment = "cheque-melenchon2022-evenements"

    order = "AFCP JLM 2022"
    address = ["Mélenchon 2022 — Service Événement", "25 passage Dubail", "75010 Paris"]

    additional_information = (
        "Votre versement ne sera confirmé qu'à réception du chèque. Vous recevrez un message de confirmation quand ce "
        " sera fait."
    )
