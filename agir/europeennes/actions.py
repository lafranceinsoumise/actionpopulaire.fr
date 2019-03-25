from pathlib import Path
from num2words import num2words

import subprocess
from django.template.loader import get_template
from django.utils.safestring import mark_safe
from markdown import markdown
from markdown.extensions.toc import TocExtension

from agir.lib.display import display_price


def display_place_of_birth(contract_information):
    if contract_information["country_of_birth"] == "FR":
        return f'{contract_information["city_of_birth"]} ({contract_information["departement_of_birth"]})'
    else:
        return f'{contract_information["city_of_birth"]} ({contract_information["country_of_birth"]}'


def display_full_address(contract_information):
    return (
        f'{contract_information["location_address1"]} {contract_information["location_address2"]} '
        f'{contract_information["location_zip"]} {contract_information["location_city"]} '
        f'{contract_information["location_country"]} '
    )


FINAL_E = {"M": "", "F": "e", "O": "⋅e"}
LENDER = {"M": "prêteur", "F": "prêteuse", "O": "prêteur⋅euse"}
ARTICLE = {"M": "le", "F": "la", "O": "le-la"}
PRONOUN = {"M": "il", "F": "elle", "O": "il-elle"}
DETERMINANT = {"M": "du", "F": "de la", "O": "du/de la"}
PAYMENT = {
    "check_afce": "chèque bancaire tiré de son compte personnel",
    "system_pay_afce": "paiement par carte bancaire depuis son compte personnel",
}


def generate_html_contract(contract_information, baselevel=1):
    gender = contract_information["gender"]

    contract_markdown = get_template("europeennes/loans/contract.md").render(
        context={
            "lender_date_of_birth": "XX/XX/XXXX",
            "lender_place_of_birth": "XXXXXXX",
            "name": f'{contract_information["first_name"]} {contract_information["last_name"]}',
            "address": "personal address",
            "date_of_birth": contract_information["date_of_birth"],
            "place_of_birth": display_place_of_birth(contract_information),
            "full_address": display_full_address(contract_information),
            "amount_letters": num2words(contract_information["amount"] / 100, lang="fr")
            + " euros",
            "amount_figure": display_price(contract_information["amount"]),
            "signature_date": contract_information.get("signature_date", "XX/XX/XXXX"),
            "e": FINAL_E[gender],
            "preteur": LENDER[gender],
            "le": ARTICLE[gender],
            "Le": ARTICLE[gender].capitalize(),
            "du": DETERMINANT[gender],
            "il": PRONOUN[gender],
            "mode_paiement": PAYMENT[contract_information["payment_mode"]],
        }
    )

    return mark_safe(
        markdown(
            contract_markdown, extensions=["extra", TocExtension(baselevel=baselevel)]
        )
    )


def save_pdf_contract(contract_information, dest_path):
    dest_dir = Path(dest_path).parent
    dest_dir.mkdir(parents=True, exist_ok=True)

    html_contract = generate_html_contract(contract_information)
    contract_with_layout = get_template(
        "europeennes/loans/contract_layout.html"
    ).render(context={"contract_body": mark_safe(html_contract)})

    proc = subprocess.Popen(
        ["wkhtmltopdf", "--encoding", "utf-8", "-", str(dest_path)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        out, errs = proc.communicate(input=contract_with_layout.encode(), timeout=10)
        return_code = proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.communicate()
        raise

    if return_code != 0:
        raise RuntimeError(f"PDF conversion failed\nOUT: {out}\nERR: {errs}")
