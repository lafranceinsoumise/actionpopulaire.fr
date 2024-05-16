from django_countries import countries

SUBSTITUTIONS = {
    "cher": {"M": "Cher", "F": "Chère", "O": "Cher·e"},
    "cher_preteur": {
        "M": "Cher prêteur",
        "F": "Chère prêteuse",
        "O": "Cher⋅e prêteur⋅se",
    },
    "final_e": {"M": "", "F": "e", "O": "⋅e"},
    "preteur": {"M": "prêteur", "F": "prêteuse", "O": "prêteur⋅euse"},
    "emprunteur": {"M": "emprunteur", "F": "emprunteuse", "O": "emprunteur⋅se"},
    "article": {"M": "le", "F": "la", "O": "le-la"},
    "pronom": {"M": "il", "F": "elle", "O": "il-elle"},
    "determinant": {"M": "du", "F": "de la", "O": "du/de la"},
    "payment": {
        "payment_card": "paiement par carte bancaire depuis son compte personnel",
        "check": "chèque bancaire tiré de son compte personnel",
    },
}


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
