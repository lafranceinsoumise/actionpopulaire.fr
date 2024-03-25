import datetime
from pathlib import Path
from typing import Mapping, Iterable
from uuid import uuid4

from django.template.loader import get_template
from django.utils.safestring import mark_safe
from markdown import markdown
from markdown.extensions.toc import TocExtension
from sepaxml import SepaTransfer

from agir.lib.documents import html_to_pdf
from agir.lib.iban import to_iban
from agir.payments.models import Payment


def generate_html_contract(payment_type, contract_information, baselevel=1):
    contract_markdown = get_template(payment_type.contract_template_name).render(
        context=payment_type.contract_context_generator(contract_information)
    )

    return mark_safe(
        markdown(
            contract_markdown, extensions=["extra", TocExtension(baselevel=baselevel)]
        )
    )


def save_pdf_contract(payment_type, contract_information, dest_path):
    dest_dir = Path(dest_path).parent
    dest_dir.mkdir(parents=True, exist_ok=True)

    html_contract = generate_html_contract(payment_type, contract_information)
    contract_with_layout = get_template(payment_type.pdf_layout_template_name).render(
        context={"contract_body": mark_safe(html_contract)}
    )

    html_to_pdf(contract_with_layout, dest_path)


def generate_reimbursement_file(config: Mapping[str, str], payments: Iterable[Payment]):
    config = dict(config)
    config.setdefault("batch", True)
    config.setdefault("currency", "EUR")

    today = datetime.date.today()

    sepa = SepaTransfer(config, clean=True)

    for payment in payments:
        iban = to_iban(payment.meta.get("iban"))

        if not iban.is_valid():
            raise ValueError(f"L'IBAN pour le paiement {payment!r} n'est pas valide")

        bic = payment.meta.get("bic", iban.bic)
        if bic is None:
            raise ValueError(f"Le BIC pour le paiement {payment!r} est inconnu")

        rembourse = payment.meta.get("rembourse", 0)
        amount = payment.price - rembourse

        if amount <= 0:
            continue

        transfer_id = str(uuid4()).replace("-", "")

        sepa.add_payment(
            {
                "name": f"{payment.first_name} {payment.last_name}",
                "IBAN": iban.as_stored_value,
                "BIC": bic,
                "amount": payment.price - rembourse,
                "execution_date": today,
                "description": f"RBST PRET {payment.id} {payment.last_name.upper()}",
                "endtoend_id": transfer_id,
            }
        )

        payment.meta["sepa_id"] = transfer_id
        payment.save()

    return sepa.export(validate=True)
