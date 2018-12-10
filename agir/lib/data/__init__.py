import csv

import os
import re
from django.db.models import Q
from functools import reduce
from operator import or_
from unidecode import unidecode

with open(os.path.dirname(os.path.realpath(__file__)) + "/departements.csv") as file:
    departements = list(csv.DictReader(file))

with open(os.path.dirname(os.path.realpath(__file__)) + "/regions.csv") as file:
    regions = list(csv.DictReader(file))


departements_choices = tuple((d["id"], f'{d["id"]} - {d["nom"]}') for d in departements)

regions_choices = tuple(
    (r["id"], r["nom"]) for r in sorted(regions, key=lambda d: unidecode(d["nom"]))
)


_CORSE_RE = re.compile("^[A|B]")


def filtre_departement(code):
    return Q(location_zip__startswith=_CORSE_RE.sub("0", code))


def filtre_region(code):
    return reduce(
        or_, (filtre_departement(d["id"]) for d in departements if d["region"] == code)
    )
