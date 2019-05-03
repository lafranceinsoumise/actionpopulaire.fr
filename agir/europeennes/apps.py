from django.apps import AppConfig

from ..payments.types import register_payment_type


class EuropeennesConfig(AppConfig):
    name = "agir.europeennes"

    DONATION_PAYMENT_TYPE = "don_europennes"
    LOAN_PAYMENT_TYPE = "pret_europeennes"

    def ready(self):
        from .views import (
            LoanReturnView,
            loan_notification_listener,
            DonationReturnView,
            donation_notification_listener,
        )

        register_payment_type(
            self.DONATION_PAYMENT_TYPE,
            "Don pour la campagne européenne",
            DonationReturnView.as_view(),
            status_listener=donation_notification_listener,
            description_template="europeennes/donations/description.html",
        )

        register_payment_type(
            self.LOAN_PAYMENT_TYPE,
            "Prêt pour la campagne européenne",
            LoanReturnView.as_view(),
            status_listener=loan_notification_listener,
            description_template="europeennes/loans/description.html",
        )
