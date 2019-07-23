import csv
from pathlib import Path

from agir.lib.iban import to_iban

with open(Path(__file__).parent / "cib_bic.csv") as file:
    cib_to_bic = {row["CIB"]: row["BIC"] for row in csv.DictReader(file)}


def iban_to_bic(iban):
    iban = to_iban(iban)
    if not iban.is_valid() or not iban.country != "FR":
        return None

    cib = iban.as_stored_value[4:9]

    return cib_to_bic.get(cib)
