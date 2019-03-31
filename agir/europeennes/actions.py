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
        "check_afce": "chèque bancaire tiré de son compte personnel",
        "system_pay_afce_pret": "paiement par carte bancaire depuis son compte personnel",
    },
}


def generate_html_contract(contract_information, baselevel=1):
    gender = contract_information["gender"]
    signed = "signature_datetime" in contract_information

    signature_image_path = (
        Path(__file__)
        .parent.joinpath("static", "europeennes", "signature_manon_aubry.png")
        .absolute()
        .as_uri()
    )

    contract_markdown = get_template("europeennes/loans/contract.md").render(
        context={
            "lender_date_of_birth": "22/12/1989",
            "lender_place_of_birth": "Fréjus (Var)",
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
            "mode_paiement": SUBSTITUTIONS["payment"][
                contract_information["payment_mode"]
            ],
            "signature": f"Accepté en ligne le {contract_information['acceptance_datetime']}"
            if signed
            else "",
            "signature_emprunteuse": mark_safe(
                f'<img title="Signature de Manon Aubry" src="{signature_image_path}">'
            )
            if signed
            else "",
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
