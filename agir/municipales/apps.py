from django.apps import AppConfig


class MunicipalesConfig(AppConfig):
    name = "agir.municipales"

    def ready(self):
        from . import payment_type

        payment_type.register_municipales_loan_payment_type()
