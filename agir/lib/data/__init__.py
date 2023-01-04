import csv
from importlib.resources import open_text

import re
from django.db.models import Q
from functools import reduce
from operator import or_
from unidecode import unidecode


def _normalize_entity_name(name):
    return unidecode(str(name)).lower().replace("-", " ")


with open_text("agir.lib.data", "departements.csv") as file:
    departements = list(csv.DictReader(file))

with open_text("agir.lib.data", "regions.csv") as file:
    regions = list(csv.DictReader(file))

for region in regions:
    region["alias"] = region["alias"].split("/") if region["alias"] else []

with open_text("agir.lib.data", "anciennes_regions.csv") as file:
    anciennes_regions = list(csv.DictReader(file))

departements_par_code = {d["id"]: d for d in departements}
departements_choices = tuple((d["id"], f'{d["id"]} - {d["nom"]}') for d in departements)
departements_par_nom = {_normalize_entity_name(d["nom"]): d for d in departements}

zones_fe_choices = (
    "Afrique centrale, australe et orientale",
    "Afrique du Nord",
    "Afrique occidentale",
    "Allemagne, Autriche, Slovaquie, Slovénie, Suisse",
    "Amérique latine et Caraïbes",
    "Asie centrale et Moyen-Orient",
    "Asie et Océanie",
    "Bénélux",
    "Canada",
    "Etats-Unis d'Amérique",
    "Europe centrale et orientale (y compris Russie)",
    "Europe du Nord",
    "Europe du Sud",
    "Israël et Territoires palestiniens",
    "Péninsule ibérique",
)

regions_par_code = {r["id"]: r for r in regions}

regions_par_nom = {_normalize_entity_name(r["nom"]): r for r in regions}

for r in regions:
    regions_par_nom.update({_normalize_entity_name(alias): r for alias in r["alias"]})


# utiliser unidecode permet de classer Île-de-France à I
regions_choices = tuple(
    (r["id"], r["nom"]) for r in sorted(regions, key=lambda d: unidecode(d["nom"]))
)

anciennes_regions_par_code = {r["id"]: r for r in anciennes_regions}

_CORSE_RE = re.compile("[ABab]")


def filtre_departements(*codes):
    return reduce(lambda a, b: a | b, (filtre_departement(code) for code in codes))


def filtre_departement(code):
    if code in departements_par_code:
        return Q(
            location_country__in=FRANCE_COUNTRY_CODES,
            location_zip__startswith=_CORSE_RE.sub("0", code),
        )

    elif _normalize_entity_name(code) in departements_par_nom:
        return Q(
            location_country__in=FRANCE_COUNTRY_CODES,
            location_zip__startswith=_CORSE_RE.sub(
                "0", departements_par_nom[_normalize_entity_name(code)]["id"]
            ),
        )

    else:
        raise ValueError("Département inconnu")


def filtre_region(code):
    if code not in regions_par_code:
        if _normalize_entity_name(code) not in regions_par_nom:
            raise ValueError(f"Région '{code}' inconnue")
        code = regions_par_nom[_normalize_entity_name(code)]["id"]

    return reduce(
        or_, (filtre_departement(d["id"]) for d in departements if d["region"] == code)
    )


def departement_from_zipcode(zipcode, fallback_value=None):
    if not zipcode:
        return fallback_value
    if zipcode.startswith("97"):
        return departements_par_code.get(zipcode[:3], fallback_value)
    # on retourne toujours par défaut le premier département Corse
    if zipcode[:2] == "20":
        zipcode = "2A"
    return departements_par_code.get(zipcode[:2], fallback_value)


def french_zipcode_to_country_code(zipcode):
    if zipcode == "97133":
        return "BL"  # Saint-Barthélémy
    if zipcode == "97150":
        return "MF"

    return OVERSEAS_ZIP_TO_COUNTRY_CODE.get(zipcode[:3], "FR")


OVERSEAS_ZIP_TO_COUNTRY_CODE = {
    "971": "GP",
    "972": "MQ",
    "973": "GF",
    "974": "RE",
    "975": "PM",
    "976": "YT",
    "984": "TF",
    "986": "WF",
    "987": "PF",
    "988": "NC",
}


FRANCE_COUNTRY_CODES = [
    "FR",  # France
    "GF",  # Guyane française
    "PF",  # Polynésie française
    "TF",  # Terres-Australes et Antarctiques
    "BL",  # Saint-Barthélémy
    "MF",  # Saint-Martin
    "PM",  # Saint-Pierre-et-Miquelon
    "GP",  # Guadeloupe
    "MQ",  # Martinique
    "YT",  # Mayotte
    "RE",  # La Réunion
    "NC",  # Nouvelle Calédonie
    "WF",  # Wallis-et-Futuna
    "",  # des fois on a pas le pays
]
