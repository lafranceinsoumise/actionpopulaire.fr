import dataclasses
import secrets
from datetime import date
from typing import Optional, List

import base64
from sepaxml import SepaTransfer

from agir.lib.iban import IBAN


def generer_endtoend_id():
    return base64.b64encode(secrets.token_bytes(26)).rstrip(b"=").decode("ascii")


@dataclasses.dataclass
class Partie:
    nom: str
    iban: IBAN
    bic: Optional[str] = None


@dataclasses.dataclass
class Virement:
    beneficiaire: Partie
    montant: int
    date_execution: date
    description: str
    id: str = dataclasses.field(default_factory=generer_endtoend_id)


def generer_fichier_virement(
    emetteur: Partie,
    virements: List[Virement],
    *,
    currency: str = "EUR",
    batch: bool = False,
    check: bool = True,
) -> bytes:
    if not emetteur.iban.is_valid():
        raise ValueError("L'IBAN émetteur n'est pas valide.")

    beneficiaires_invalides = [
        v.beneficiaire.nom for v in virements if not v.beneficiaire.iban.is_valid()
    ]

    if beneficiaires_invalides:
        beneficiaires_invalides = ",".join(f"« {b} »" for b in beneficiaires_invalides)
        raise ValueError(
            f"Les IBAN des émetteurs suivants sont invalides : {beneficiaires_invalides}."
        )

    fichier_sepa = SepaTransfer(
        {
            "name": emetteur.nom,
            "IBAN": emetteur.iban.as_stored_value,
            "BIC": emetteur.bic or emetteur.iban.bic,
            "batch": batch,
            "currency": currency,
        },
        # de façon bizarre, SepaTransfer utilise parfois la norme allemande à la place de l'européenne
        # si ce n'est pas précisé.
        schema="pain.001.001.03",
        clean=True,
    )

    for virement in virements:
        fichier_sepa.add_payment(
            {
                "name": virement.beneficiaire.nom,
                "IBAN": virement.beneficiaire.iban.as_stored_value,
                "BIC": virement.beneficiaire.bic or virement.beneficiaire.iban.bic,
                "amount": virement.montant,
                "execution_date": virement.date_execution,
                "description": virement.description,
                "endtoend_id": virement.id,
            }
        )

    return fichier_sepa.export(validate=check)
