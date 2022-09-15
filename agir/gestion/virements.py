import dataclasses
import secrets
from datetime import date
from typing import Optional, List

import base64

from lxml import etree
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
    paiement_unique: bool = True,
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
            "batch": paiement_unique,
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

    xml_content = fichier_sepa.export(validate=check)

    if paiement_unique and not batch:
        prolog = b'<?xml version="1.0" encoding="UTF-8"?>'
        NS = "{urn:iso:std:iso:20022:tech:xsd:pain.001.001.03}"
        root_elem = etree.fromstring(xml_content)
        root_tree = root_elem.getroottree()
        batch_elem = root_tree.find(f"//{NS}BtchBookg")
        batch_elem.text = "false"

        xml_content = prolog + etree.tostring(root_elem, encoding="utf-8")

    return xml_content


def virements_depuis_dataframe(
    df, *, iban, nom, description, montant, date_execution=None
):
    if date_execution is None:
        date_execution = date.today()

    recipients = [
        Partie(
            nom=r[nom],
            iban=IBAN(r[iban]),
        )
        for _, r in df.iterrows()
    ]

    iban_invalide = [i for i, p in enumerate(recipients) if not p.iban.is_valid()]

    if iban_invalide:
        base_message = "Certains IBAN ne sont pas valides :"
        message = "\n".join(f"{i+2}: {recipients[i].nom}" for i in iban_invalide)

        raise ValueError(f"{base_message}\n{message}")

    bic_inconnu = [i for i, p in enumerate(recipients) if not hasattr(p.iban, "bic")]

    if bic_inconnu:
        base_message = "Les BIC ne sont pas connus pour les IBAN suivants :"
        message = "\n".join(f"{i+2}: {recipients[i].iban}" for i in bic_inconnu)
        raise ValueError(f"{base_message}\n{message}")

    virements = [
        Virement(
            beneficiaire=p,
            montant=round(r[montant] * 100),
            date_execution=date_execution,
            description=r[description],
        )
        for p, (_, r) in zip(recipients, df.iterrows())
    ]

    return virements
