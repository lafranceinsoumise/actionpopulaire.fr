from django.apps import AppConfig

from ..payments.types import register_payment_type


class EuropeennesConfig(AppConfig):
    name = "agir.europeennes"

    LOAN_PAYMENT_TYPE = "pret_europeennes"

    def ready(self):
        from .views import LoanReturnView, loan_notification_listener

        register_payment_type(
            self.LOAN_PAYMENT_TYPE,
            "Prêt pour la campagne européenne",
            LoanReturnView.as_view(),
            status_listener=loan_notification_listener,
        )
