import csv

import os
import re
from django.db.models import Q
from functools import reduce
from operator import or_
from unidecode import unidecode


def _normalize_entity_name(name):
    return unidecode(str(name)).lower().replace("-", " ")


with open(os.path.dirname(os.path.realpath(__file__)) + "/departements.csv") as file:
    departements = list(csv.DictReader(file))

with open(os.path.dirname(os.path.realpath(__file__)) + "/regions.csv") as file:
    regions = list(csv.DictReader(file))

for region in regions:
    region["alias"] = region["alias"].split("/") if region["alias"] else []

with open(
    os.path.dirname(os.path.realpath(__file__)) + "/anciennes_regions.csv"
) as file:
    anciennes_regions = list(csv.DictReader(file))

departements_map = {d["id"]: d for d in departements}
departements_choices = tuple((d["id"], f'{d["id"]} - {d["nom"]}') for d in departements)

regions_map = {
    **{r["id"]: r for r in regions},
    **{_normalize_entity_name(r["nom"]): r for r in regions},
}

for r in regions:
    regions_map.update({_normalize_entity_name(alias): r for alias in r["alias"]})


# utiliser unidecode permet de classer Île-de-France à I
regions_choices = tuple(
    (r["id"], r["nom"]) for r in sorted(regions, key=lambda d: unidecode(d["nom"]))
)

anciennes_regions_map = {r["id"]: r for r in anciennes_regions}

_CORSE_RE = re.compile("^[A|B]")


def filtre_departement(code):
    return Q(location_zip__startswith=_CORSE_RE.sub("0", code))


def filtre_region(code):
    code = regions_map[_normalize_entity_name(code)]["id"]

    return reduce(
        or_, (filtre_departement(d["id"]) for d in departements if d["region"] == code)
    )


def departement_from_zipcode(zipcode):
    if zipcode.startswith("97"):
        return departements_map.get(zipcode[:3], None)

    # on retourne toujours par défaut le premier département Corse
    if zipcode[:2] == "20":
        zipcode = "2A"
    return departements_map.get(zipcode[:2], None)


FRANCE_COUNTRY_CODES = [
    "FR",  # France
    "GF",  # Guyane française
    "PF",  # Polynésie française
    "TF",  # Territoires australs
    "BL",  # Saint-Barthélémy
    "MF",  # Saint-Martin
    "PM",  # Saint-Pierre-et-Miquelon
    "GP",  # Guadeloupe
    "MQ",  # Martinique
    "YT",  # Mayotte
    "RE",  # Réunion
    "NC",  # Nouvelle Calédonie
    "WF",  # Wallis-et-Futuna
]
