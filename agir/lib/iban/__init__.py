import csv
import logging
import re
import string
from importlib.resources import open_text

from django.core import validators

from schwifty import IBAN as IBAN_schwifty

BIC_REGEX = re.compile(
    r"^(?P<banque>[A-Z]{4})(?P<pays>[A-Z]{2})(?P<localisation>[A-Z0-9]{2})(?P<filiale>[A-Z0-9]{3})?"
)


logger = logging.getLogger(__name__)


def _iban_regex(s: str):
    raw = s.replace("d", "[0-9]").replace("l", "[A-Z]").replace("a", "[A-Z0-9]")
    return re.compile(f"^{raw}$")


with open_text("agir.lib.iban", "formats_iban.csv") as fd:
    IBAN_REGEX_NATIONALES = {
        country["code"]: _iban_regex(country["regex"]) for country in csv.DictReader(fd)
    }


CIB_TO_BIC = None


def bic_from_cib(cib):
    global CIB_TO_BIC
    if CIB_TO_BIC is None:
        with open_text("agir.lib.iban", "conversion_cib_bic.csv") as f:
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
        try:
            return bic_from_cib(self.value[4:9])
        except KeyError:
            """
            use IBAN schwifty en tant qu'alternative,
            remplacer cette classe d'utils une fois que schwifty supporte nos banques
            PR on progress https://github.com/mdomke/schwifty/pull/224
            """
            return IBAN_schwifty(self.value).bic

    def __init__(self, value):
        self.value = re.sub(r"\s+", "", value).upper()

    def _get_modulo(self):
        # 1. on déplace les 4 premiers symboles à la fin
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
        # respect du format général d'un IBAN
        if not self.regex.match(self.value):
            return False

        code_pays = self.value[:2]
        partie_nationale = self.value[4:]

        # le code pays doit être correct
        if code_pays not in IBAN_REGEX_NATIONALES:
            return False

        # la partie nationale doit satisfaire la regex nationale
        if not IBAN_REGEX_NATIONALES[code_pays].match(partie_nationale):
            return False

        # le checksum doit être correct
        return self._get_modulo() == 1

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


class BIC:
    regex = BIC_REGEX
    value = ""
    match = None

    @property
    def parts(self):
        if not self.match:
            return {}

        return self.match.groupdict()

    @property
    def business_party_prefix(self):
        return self.parts.get("banque", None)

    @property
    def country(self):
        return self.parts.get("pays", None)

    @property
    def business_party_suffix(self):
        return self.parts.get("localisation", None)

    @property
    def branch(self):
        return self.parts.get("filiale", None)

    @property
    def as_stored_value(self):
        return self.value

    def __init__(self, value):
        self.value = re.sub(r"\s+", "", str(value)).upper()
        self.match = self.regex.fullmatch(self.value)

    def is_valid(self):
        return self.match is not None

    def __str__(self):
        return self.value

    def __repr__(self):
        return "BIC('{}')".format(str(self))

    def __eq__(self, other):
        return isinstance(other, BIC) and self.value == other.value

    def __len__(self):
        return len(self.value)


def to_bic(s):
    if isinstance(s, BIC) or s in validators.EMPTY_VALUES:
        return s

    if not isinstance(s, str):
        s = str(s)

    return BIC(s)
