from django.apps import AppConfig

from payments.types import register_payment_type


class DonsConfig(AppConfig):
    name = "donations"

    def ready(self):
        from .views import ReturnView
        register_payment_type('don', 'Don', ReturnView.as_view())
