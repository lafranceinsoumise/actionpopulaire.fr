import csv
import dataclasses
import json
import re
from functools import reduce
from importlib.resources import open_text
from operator import or_

from django.db.models import Q, IntegerChoices
from glom import glom
from unidecode import unidecode


class TypeNom(IntegerChoices):
    """Nomenclature des noms propres utilisés par l'INSEE pour les noms de lieu

    Cette nomenclature permet de savoir quels sont les articles et les charnières applicables
    aux noms propres de communes, départements et régions.

    Référence :
    https://www.insee.fr/fr/information/2560684#tncc
    """

    def __new__(cls, value, article, charniere):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.article = article
        obj.charniere = charniere
        return obj

    CONSONNE = 0, "", "de ", "Pas d'article, commence par une consonne (sauf H muet)"
    VOYELLE = 1, "", "d'", "Pas d'article, commence par une voyelle (ou H muet)"
    ARTICLE_LE = 2, "le ", "du ", "Article = LE"
    ARTICLE_LA = 3, "la ", "de la ", "Article = LA"
    ARTICLE_LES = 4, "les ", "des ", "Article = LES"
    ARTICLE_L = 5, "l'", "de l'", "Article = L'"
    ARTICLE_AUX = 6, "aux", "des ", "Article = AUX"
    ARTICLE_LAS = 7, "las ", "de las ", "Article = LAS"
    ARTICLE_LOS = 8, "los ", "de los ", "Article = LOS"


class AvecTypeNom:
    @property
    def nom_complet(self):
        """Retourne le nom complet de l'entité, avec l'article éventuel.

        :return: Le nom complet de l'entité, avec l'article si approprié.
        """
        return f"{self.type_nom.article}{self.nom}"

    @property
    def nom_avec_charniere(self):
        """Retourne le nom de l'entité précédé de la charnière (forme possessive).

        :return: le nom avec la charniere (par exemple "de la Charente")
        """
        return f"{self.type_nom.charniere}{self.nom}"


@dataclasses.dataclass(frozen=True)
class Departement(AvecTypeNom):
    id: str
    nom: str
    code_region: str
    code_ancienne_region: str
    type_nom: TypeNom

    def __str__(self):
        return f"{self.id} — {self.nom_complet}"

    @property
    def nom_region(self):
        if self.code_region:
            return regions_par_code[self.code_region].nom
        return ""

    @property
    def nom_ancienne_region(self):
        if self.code_ancienne_region:
            return anciennes_regions_par_code[self.code_ancienne_region].nom
        return ""

    @property
    def filtre(self):
        return filtre_departement(self.id)


@dataclasses.dataclass
class Region(AvecTypeNom):
    id: str
    nom: str
    type_nom: TypeNom
    alias: list[str]

    def __str__(self):
        return self.nom


spec_departement = {
    "id": "id",
    "nom": "nom",
    "code_region": "region",
    "code_ancienne_region": "ancienne_region",
    "type_nom": ("tncc", int, TypeNom),
}

spec_region = {
    "id": "id",
    "nom": "nom",
    "type_nom": ("tncc", int, TypeNom),
    "alias": lambda r: r["alias"].split("/") if r["alias"] else [],
}

spec_ancienne_region = spec_region.copy()
spec_ancienne_region["alias"] = lambda _: []


def _normalize_entity_name(name):
    return unidecode(str(name)).lower().replace("-", " ")


with open_text("agir.lib.data", "departements.csv") as file:
    departements: list[Departement] = [
        Departement(**r) for r in glom(csv.DictReader(file), [spec_departement])
    ]

with open_text("agir.lib.data", "regions.csv") as file:
    regions = [Region(**r) for r in glom(csv.DictReader(file), [spec_region])]

with open_text("agir.lib.data", "anciennes_regions.csv") as file:
    anciennes_regions = [
        Region(**r) for r in glom(csv.DictReader(file), [spec_ancienne_region])
    ]

with open_text("agir.lib.data", "circonscriptionsFE.json") as file:
    circos_fe = json.load(file)

departements_par_code: dict[str, Departement] = {d.id: d for d in departements}
departements_choices = tuple((d.id, f"{d.id} - {d.nom}") for d in departements)
departements_par_nom = {_normalize_entity_name(d.nom): d for d in departements}

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
    "États-Unis d'Amérique",
    "Europe centrale et orientale (y compris Russie)",
    "Europe du Nord",
    "Europe du Sud",
    "Israël et Territoires palestiniens",
    "Péninsule ibérique",
)

circo_fe_choices = tuple(
    (circo_fe["code"], f"{circo_fe['code']} · {circo_fe['nom']}")
    for circo_fe in circos_fe
)

departements_or_zones_fe_choices = departements_choices + tuple(
    (zone_fe, f"99 - {zone_fe}") for zone_fe in zones_fe_choices
)

departements_or_circo_fe_choices = departements_choices + circo_fe_choices

# Reverse dictionary with labels as keys and ids as values
departements_or_circo_fe_reverse_choices = dict(
    departement[::-1] for departement in departements_or_circo_fe_choices
)

regions_par_code = {r.id: r for r in regions}
regions_par_nom = {_normalize_entity_name(r.nom): r for r in regions}

for r in regions:
    regions_par_nom.update({_normalize_entity_name(alias): r for alias in r.alias})


# utiliser unidecode permet de classer Île-de-France à I
regions_choices = tuple(
    (r.id, r.nom) for r in sorted(regions, key=lambda d: unidecode(d.nom))
)

anciennes_regions_par_code = {r.id: r for r in anciennes_regions}

_CORSE_RE = re.compile("[ABab]")


def filtre_departements(*codes):
    return reduce(lambda a, b: a | b, (filtre_departement(code) for code in codes))


def filtre_departement(code):
    if code in departements_par_code:
        return Q(location_country__in=FRANCE_COUNTRY_CODES) & (
            Q(
                location_departement_id="",
                location_zip__startswith=_CORSE_RE.sub("0", code),
            )
            | Q(location_departement_id=code)
        )

    elif _normalize_entity_name(code) in departements_par_nom:
        return Q(
            location_country__in=FRANCE_COUNTRY_CODES,
            location_zip__startswith=_CORSE_RE.sub(
                "0", departements_par_nom[_normalize_entity_name(code)].id
            ),
        )

    else:
        raise ValueError("Département inconnu")


def filtre_region(code):
    if code not in regions_par_code:
        if _normalize_entity_name(code) not in regions_par_nom:
            raise ValueError(f"Région '{code}' inconnue")
        code = regions_par_nom[_normalize_entity_name(code)].id

    return reduce(or_, (filtre_departement(d.id) for d in departements if d.id == code))


def code_postal_vers_code_departement(zipcode: str) -> str:
    if zipcode.startswith("97"):
        code = zipcode[:3]
    # on retourne toujours par défaut le premier département Corse
    elif zipcode[:2] == "20":
        code = "2A"
    else:
        code = zipcode[:2]

    if code in departements_par_code:
        return code
    return ""


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
    "NC",  # Nouvelle-Calédonie
    "WF",  # Wallis-et-Futuna
    "",  # en cas d'absence du pays,
]
