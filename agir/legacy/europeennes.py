from uuid import uuid4
from django.http import Http404

from agir.loans.loan_config import LoanConfiguration
from agir.payments.types import register_payment_type, PaymentType


def not_found(request, payment):
    raise Http404()


register_payment_type(
    PaymentType(
        "don_europeennes",
        "Don à la campagne européenne 2019",
        not_found,
        description_template="legacy/europeennes/donation_description.html",
    )
)


def contract_path(payment):
    return f"europeennes/loans/{payment.id}/{uuid4()}.pdf"


register_payment_type(
    LoanConfiguration(
        id="pret_europeennes",
        label="Prêt à la campagne européenne 2019",
        loan_recipient="l'AFCE LFI 2019",
        description_template="legacy/europeennes/loan_description.html",
        contract_path=contract_path,
        contract_template_name="legacy/europeennes/contract.md",
        pdf_layout_template_name="legacy/europeennes/contract_layout.html",
    )
)
