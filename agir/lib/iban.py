import csv
import re
import string
from importlib.resources import open_text

from django.core import validators


CIB_TO_BIC = None


def bic_from_cib(cib):
    global CIB_TO_BIC
    if CIB_TO_BIC is None:
        with open_text("agir.lib.data", "conversion_cib_bic.csv") as f:
            r = csv.DictReader(f)
            CIB_TO_BIC = {b["CIB"]: b["BIC"] for b in r}

    return CIB_TO_BIC[cib]


class IBAN:
    regex = re.compile(r"^[A-Z]{2}[0-9]{2}[A-Z0-9]{10,30}$")

    _symbol_value_table = {
        **{str(i): str(i) for i in range(0, 10)},
        **{
            c: str(v)
            for c, v in zip(
                string.ascii_uppercase, range(10, 10 + len(string.ascii_uppercase))
            )
        },
    }

    @property
    def as_stored_value(self):
        return self.value

    @property
    def country(self):
        return self.value[:2]

    @property
    def bic(self):
        if self.country != "FR":
            raise AttributeError("Pas de BIC automatique pour les IBAN non-français")

        try:
            return bic_from_cib(self.value[4:9])
        except KeyError:
            raise AttributeError("BIC inconnu pour cette banque")

    def __init__(self, value):
        self.value = value.translate(str.maketrans("", "", string.whitespace)).upper()

    def _get_modulo(self):
        # 1. on déplace les 4 premiers symbole à la fin
        # 2. on substitue à chaque lettre deux chiffres selon la règle A=10, B=11, C=12
        # 3. cela nous donne un grand entier (plus long)
        # 4. on vérifie que ce grand entier est bien congruent à 1 modulo 97
        subst = int(
            "".join(
                self._symbol_value_table[c] for c in self.value[4:] + self.value[:4]
            )
        )
        return subst % 97

    def is_valid(self):
        return self.regex.match(self.value) and self._get_modulo() == 1

    def __str__(self):
        return " ".join(self.value[i : i + 4] for i in range(0, len(self.value), 4))

    def __repr__(self):
        return "IBAN('{}')".format(str(self))

    def __eq__(self, other):
        return isinstance(other, IBAN) and self.value == other.value


def to_iban(s):
    if isinstance(s, IBAN) or s in validators.EMPTY_VALUES:
        return s

    if not isinstance(s, str):
        s = str(s)

    return IBAN(s)
