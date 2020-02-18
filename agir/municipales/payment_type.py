from uuid import uuid4

from django.utils.html import format_html

from agir.loans.display import SUBSTITUTIONS
from agir.loans.loan_config import LoanConfiguration, default_contract_context_generator
from agir.municipales.models import CommunePage
from agir.municipales.views import CommuneLoanReturnView
from agir.payments.payment_modes import PAYMENT_MODES
from agir.payments.types import register_payment_type


def contract_path(payment):
    return f"municipales/loans/{payment.id}/{uuid4()}.pdf"


def contract_context_generator(contract_information):
    context = default_contract_context_generator(contract_information)
    payment_mode = PAYMENT_MODES[contract_information["payment_mode"]]
    campagne = payment_mode.campagne
    commune = CommunePage.objects.get(
        code_departement=campagne["code_departement"], slug=campagne["slug"]
    )

    signed = "signature_datetime" in contract_information
    if signed:
        signature_emprunteur = format_html(
            '<img src="{src}" alt="{alt}">',
            src=campagne["signature_image"],
            alt=f'Signature de la tête de liste {campagne["nom_emprunteur"]}',
        )
    else:
        signature_emprunteur = ""

    context.update(
        {
            "nom_emprunteur": campagne["nom_emprunteur"],
            "adresse_emprunteur": campagne["adresse_emprunteur"],
            "signature_emprunteur": signature_emprunteur,
            "emprunteur": SUBSTITUTIONS["emprunteur"][campagne["genre_emprunteur"]],
            "e_emprunteur": SUBSTITUTIONS["final_e"][campagne["genre_emprunteur"]],
            "mandataire": campagne["mandataire"],
            "adresse_mandataire": campagne["adresse_mandataire"],
            "nom_ville": commune.name,
        }
    )

    return context


def register_municipales_loan_payment_type():
    register_payment_type(
        LoanConfiguration(
            id="pret_municipales",
            label="Prêt à une campagne municipale 2020",
            loan_recipient="une campagne municipale 2020",
            contract_path=contract_path,
            contract_template_name="municipales/loans/contract.md",
            pdf_layout_template_name="municipales/loans/contract_layout.html",
            contract_context_generator=contract_context_generator,
            success_view=CommuneLoanReturnView.as_view(),
        )
    )
