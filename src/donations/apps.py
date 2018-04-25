from django.apps import AppConfig

from payments.types import register_payment_type


class DonsConfig(AppConfig):
    name = "donations"

    PAYMENT_TYPE = 'don'

    def ready(self):
        from .views import ReturnView
        register_payment_type(self.PAYMENT_TYPE, 'Don', ReturnView.as_view())
