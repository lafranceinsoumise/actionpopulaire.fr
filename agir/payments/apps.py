from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    name = "agir.payments"

    def ready(self):
        from .payment_modes import setup_urls

        setup_urls()
