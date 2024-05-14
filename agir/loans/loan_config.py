from pathlib import Path
from typing import Callable, Union, Mapping, Dict, Optional

from dateutil.parser import isoparse
from num2words import num2words

from agir.lib.display import display_price
from agir.lib.iban import to_iban
from agir.loans.display import (
    display_place_of_birth,
    display_full_address,
    SUBSTITUTIONS,
)
from agir.payments.models import Payment
from agir.payments.payment_modes import PAYMENT_MODES
from agir.payments.types import PaymentType, PAYMENT_TYPES


def default_description_context_generator(payment: Payment):
    payment_type = PAYMENT_TYPES[payment.type]
    iban = to_iban(payment.meta.get("iban"))

    return {
        "payment": payment,
        "iban": str(to_iban(payment.meta.get("iban"))),
        "bic": payment.meta.get("bic") or iban.bic,
        "loan_recipient": payment_type.loan_recipient,
    }


def default_contract_context_generator(
    contract_information: Mapping[str, object]
) -> Dict[str, str]:
    civilite = contract_information.get("civilite", "O")
    signed = "signature_datetime" in contract_information
    payment_mode = PAYMENT_MODES[contract_information["payment_mode"]]

    signature_date = contract_information.get("signature_datetime")
    if signature_date:
        signature_date = isoparse(signature_date).strftime("%d/%m/%Y")
    else:
        signature_date = "XX/XX/XXXX"

    # noinspection PyTypeChecker
    return {
        "nom_preteur": f'{contract_information["first_name"]} {contract_information["last_name"]}',
        "date_naissance": contract_information["date_of_birth"],
        "lieu_naissance": display_place_of_birth(contract_information),
        "adresse_preteur": display_full_address(contract_information),
        "amount_letters": num2words(contract_information["amount"] / 100, lang="fr")
        + " euros",
        "amount_figure": display_price(contract_information["amount"]),
        "signature_date": signature_date,
        "e": SUBSTITUTIONS["final_e"][civilite],
        "preteur": SUBSTITUTIONS["preteur"][civilite],
        "le": SUBSTITUTIONS["article"][civilite],
        "Le": SUBSTITUTIONS["article"][civilite].capitalize(),
        "du": SUBSTITUTIONS["determinant"][civilite],
        "il": SUBSTITUTIONS["pronom"][civilite],
        "mode_paiement": SUBSTITUTIONS["payment"][payment_mode.category],
        "signe": signed,
    }


class LoanConfiguration(PaymentType):
    def __init__(
        self,
        loan_recipient: str,
        contract_path: Callable[[Payment], Union[str, Path]],
        contract_template_name: str,
        pdf_layout_template_name: str,
        contract_context_generator: Callable[
            [Mapping[str, object]], Mapping[str, str]
        ] = default_contract_context_generator,
        min_amount: Optional[int] = None,
        max_amount: Optional[int] = None,
        global_ceiling: Optional[int] = None,
        **kwargs,
    ):
        self.loan_recipient = loan_recipient
        self.contract_path = contract_path
        self.contract_template_name = contract_template_name
        self.pdf_layout_template_name = pdf_layout_template_name
        self.contract_context_generator = contract_context_generator
        self.min_amount = min_amount
        self.max_amount = max_amount
        self.global_ceiling = global_ceiling

        from agir.loans import views

        kwargs.setdefault("status_listener", views.loan_notification_listener)
        kwargs.setdefault("description_template", "loans/description.html")
        kwargs.setdefault(
            "description_context_generator", default_description_context_generator
        )

        super().__init__(**kwargs)
