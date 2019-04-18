from django.apps import AppConfig

from ..payments.types import register_payment_type


class DonsConfig(AppConfig):
    name = "agir.donations"

    PAYMENT_TYPE = "don"

    def ready(self):
        from .views import ReturnView, notification_listener

        register_payment_type(
            self.PAYMENT_TYPE,
            "Don",
            ReturnView.as_view(),
            status_listener=notification_listener,
            description_template="donations/description.html",
        )
