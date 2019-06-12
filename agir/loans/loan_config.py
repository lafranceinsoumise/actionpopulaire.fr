from pathlib import Path
from typing import Callable, Union

from agir.payments.models import Payment
from agir.payments.types import PaymentType
from agir.loans import views


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

        super().__init__(*args, **kwargs)
