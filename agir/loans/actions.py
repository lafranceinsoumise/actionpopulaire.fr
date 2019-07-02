from pathlib import Path

from django_countries import countries
from num2words import num2words

import subprocess
from django.template.loader import get_template
from django.utils.safestring import mark_safe
from markdown import markdown
from markdown.extensions.toc import TocExtension

from agir.lib.display import display_price
from agir.payments.payment_modes import PAYMENT_MODES


def display_place_of_birth(contract_information):
    country_of_birth = countries.name(contract_information["country_of_birth"])

    if contract_information["country_of_birth"] == "FR":
        return f'{contract_information["city_of_birth"]} ({contract_information["departement_of_birth"]})'
    else:
        return f'{contract_information["city_of_birth"]} ({country_of_birth})'


def display_full_address(contract_information):
    street_address = contract_information["location_address1"]
    if contract_information["location_address2"]:
        street_address += ", " + contract_information["location_address2"]

    if contract_information["location_zip"]:
        city_address = (
            contract_information["location_zip"]
            + " "
            + contract_information["location_city"]
        )
    else:
        city_address = contract_information["location_city"]

    country_address = countries.name(contract_information["location_country"])

    return f"{street_address}, {city_address}, {country_address}"


SUBSTITUTIONS = {
    "cher_preteur": {
        "M": "Cher prêteur",
        "F": "Chère prêteuse",
        "O": "Cher⋅e prêteur⋅se",
    },
    "final_e": {"M": "", "F": "e", "O": "⋅e"},
    "lender": {"M": "prêteur", "F": "prêteuse", "O": "prêteur⋅euse"},
    "article": {"M": "le", "F": "la", "O": "le-la"},
    "pronoun": {"M": "il", "F": "elle", "O": "il-elle"},
    "determinant": {"M": "du", "F": "de la", "O": "du/de la"},
    "payment": {
        "payment_card": "paiement par carte bancaire depuis son compte personnel",
        "check": "chèque bancaire tiré de son compte personnel",
    },
}


def generate_html_contract(contract_template, contract_information, baselevel=1):
    gender = contract_information["gender"]
    signed = "signature_datetime" in contract_information
    payment_mode = PAYMENT_MODES[contract_information["payment_mode"]]

    contract_markdown = get_template(contract_template).render(
        context={
            "name": f'{contract_information["first_name"]} {contract_information["last_name"]}',
            "address": "personal address",
            "date_of_birth": contract_information["date_of_birth"],
            "place_of_birth": display_place_of_birth(contract_information),
            "full_address": display_full_address(contract_information),
            "amount_letters": num2words(contract_information["amount"] / 100, lang="fr")
            + " euros",
            "amount_figure": display_price(contract_information["amount"]),
            "signature_date": contract_information.get(
                "signature_datetime", "XX/XX/XXXX"
            ),
            "e": SUBSTITUTIONS["final_e"][gender],
            "preteur": SUBSTITUTIONS["lender"][gender],
            "le": SUBSTITUTIONS["article"][gender],
            "Le": SUBSTITUTIONS["article"][gender].capitalize(),
            "du": SUBSTITUTIONS["determinant"][gender],
            "il": SUBSTITUTIONS["pronoun"][gender],
            "mode_paiement": SUBSTITUTIONS["payment"][payment_mode.category],
            "signature": f"Accepté en ligne le {contract_information['acceptance_datetime']}"
            if signed
            else "",
            "signe": signed,
        }
    )

    return mark_safe(
        markdown(
            contract_markdown, extensions=["extra", TocExtension(baselevel=baselevel)]
        )
    )


def save_pdf_contract(
    contract_template,
    contract_information,
    dest_path,
    layout_template="loans/default_contract_layout.html",
):
    dest_dir = Path(dest_path).parent
    dest_dir.mkdir(parents=True, exist_ok=True)

    html_contract = generate_html_contract(contract_template, contract_information)
    contract_with_layout = get_template(layout_template).render(
        context={"contract_body": mark_safe(html_contract)}
    )

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
