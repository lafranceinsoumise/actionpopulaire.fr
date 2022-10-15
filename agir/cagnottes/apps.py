from django.apps import AppConfig

from agir.payments.types import (
    PaymentType,
    register_payment_type,
)


class CagnottesConfig(AppConfig):
    name = "agir.cagnottes"
    verbose_name = "Cagnottes"
    PAYMENT_TYPE = "don_cagnotte"

    def ready(self):
        from agir.donations.views import notification_listener
        from .views import RemerciementView

        register_payment_type(
            payment_type=PaymentType(
                self.PAYMENT_TYPE,
                "Don à une cagnotte",
                RemerciementView.as_view(),
                status_listener=notification_listener,
                description_template="cagnottes/description.html",
                email_template_code="DONATION_CAGNOTTE",
                email_from="Caisse de grève insoumise <nepasrepondre@lafranceinsoumise.fr>",
            )
        )
