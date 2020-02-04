from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    name = "agir.payments"

    def ready(self):
        from .payment_modes import PAYMENT_MODES, _setup_urls

        _setup_urls(PAYMENT_MODES.values())
