from pathlib import Path
from typing import Callable, Union

from agir.lib.iban import to_iban
from agir.loans.data.banks import iban_to_bic
from agir.payments.models import Payment
from agir.payments.types import PaymentType, PAYMENT_TYPES
from agir.loans import views


def default_description_context_generator(payment: Payment):
    payment_type = PAYMENT_TYPES[payment.type]
    iban = to_iban(payment.meta.get("iban"))

    return {
        "payment": payment,
        "iban": str(to_iban(payment.meta.get("iban"))),
        "bic": payment.meta.get("bic") or iban_to_bic(iban),
        "loan_recipient": payment_type.loan_recipient,
    }


class LoanConfiguration(PaymentType):
    def __init__(
        self,
        *args,
        loan_recipient: str,
        contract_path: Callable[[Payment], Union[str, Path]],
        contract_template_name: str,
        pdf_layout_template_name: str,
        thank_you_template_name: str = "loans/return.html",
        **kwargs
    ):
        self.loan_recipient = loan_recipient
        self.contract_path = contract_path
        self.contract_template_name = contract_template_name
        self.pdf_layout_template_name = pdf_layout_template_name

        kwargs.setdefault(
            "success_view",
            views.LoanReturnView.as_view(template_name=thank_you_template_name),
        )
        kwargs.setdefault("status_listener", views.loan_notification_listener)
        kwargs.setdefault("description_template", "loans/description.html")
        kwargs.setdefault(
            "description_context_generator", default_description_context_generator
        )

        super().__init__(*args, **kwargs)
