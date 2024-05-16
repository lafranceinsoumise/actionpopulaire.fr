from django.apps import AppConfig


def contract_path(payment):
    return f"europennes2024/prets/{payment.id}.pdf"


class Europeennes2024Config(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "agir.europeennes2024"

    LOAN_TYPE = "pret_europeennes2024"
    DONATION_TYPE = "don_europeennes2024"

    def ready(self):
        from agir.payments.types import (
            register_payment_type,
            PaymentType,
        )
        from agir.loans.loan_config import LoanConfiguration
        from . import views

        self.donation_type = PaymentType(
            id=self.DONATION_TYPE,
            label="Don à la campagne de Manon Aubry pour les européennes 2024",
            success_view=views.don_success_view,
            status_listener=views.don_status_listener,
        )
        register_payment_type(self.donation_type)

        self.loan_type = LoanConfiguration(
            id=self.LOAN_TYPE,
            label="Prêt à la campagne de Manon Aubry pour les européennes 2024",
            success_view=views.pret_success_view,
            loan_recipient="la campagne de Manon Aubry pour les européennes 2024",
            contract_path=contract_path,
            contract_template_name="europeennes2024/contrat.md",
            pdf_layout_template_name="europeennes2024/layout_contrat.html",
            status_listener=views.pret_status_listener,
            min_amount=300_00,
            max_amount=10_000_00,
            global_ceiling=2_000_000_00,
        )
        register_payment_type(self.loan_type)
