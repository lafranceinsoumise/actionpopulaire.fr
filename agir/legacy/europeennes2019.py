from uuid import uuid4

from agir.legacy.utils import LegacyPaymentType, not_found
from agir.loans.loan_config import LoanConfiguration
from agir.payments.types import register_payment_type, PaymentType

register_payment_type(
    LegacyPaymentType(
        id="don_europeennes",
        label="Don à la campagne européenne 2019",
        description_template="legacy/europeennes/donation_description.html",
    )
)


def contract_path(payment):
    return f"europeennes/loans/{payment.id}/{uuid4()}.pdf"


register_payment_type(
    LoanConfiguration(
        id="pret_europeennes",
        label="Prêt à la campagne européenne 2019",
        loan_recipient="la campagne européenne 2019",
        contract_path=contract_path,
        contract_template_name="legacy/europeennes/contract.md",
        pdf_layout_template_name="legacy/europeennes/contract_layout.html",
        success_view=not_found,
    )
)
