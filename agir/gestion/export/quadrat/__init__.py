import dataclasses
import datetime


def formatter_montant(m: int, l: int):
    signe = "+" if m >= 0 else "-"
    montant = str(abs(m)).zfill(l - 1)
    return f"{signe}{montant}"


def formatter_date(d: datetime.date):
    return d.strftime("%d%m%y")


def formatter_chaine(s: str, l: int):
    return s.ljust(l, " ")


ECRITURE_TEMPLATE = (
    "M"  # type d'entrée
    "{numero_compte:<8s}"
    "{code_journal:02d}"
    "000"  # numéro folio
    "{date_ecriture}"
    " "  # code libellé
    "{libelle:<20s}"
    "{debit_credit}"
    "{montant:0=+13d}"
    "{compte_contrepartie:<8s}"
    "{date_echeance}"
    "  "
    "   "
    "{numero_piece:<5s}"
)


@dataclasses.dataclass
class Ecriture:
    numero_compte: str
    code_journal: str
    date: datetime.date
    numero_piece: str
    code_insee: str
    nature: str
    quantite: int
    periode_debut: datetime.date
    periode_fin: datetime.date
    debit: bool
    montant: int

    def __str__(self):
        return Ecriture
