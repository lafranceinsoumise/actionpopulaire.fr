import base64
import dataclasses
import secrets
from datetime import date
from typing import Optional, List

import pandas as pd
from django.core.exceptions import ValidationError
from django.utils.translation import ngettext
from lxml import etree
from sepaxml import SepaTransfer

from schwifty import IBAN


def generer_endtoend_id():
    return base64.b64encode(secrets.token_bytes(26)).rstrip(b"=").decode("ascii")


@dataclasses.dataclass
class Partie:
    nom: str
    iban: IBAN
    bic: Optional[str] = None
    label: Optional[str] = None


BANK_TRANSFER_EMITTER = {
    "LFI": Partie(
        nom="LA FRANCE INSOUMISE", iban=IBAN("FR76 4255 9100 0008 0188 0226 293")
    ),
    "AFCE_LFI_2024": Partie(
        nom="AFCE LFI 2024", iban=IBAN("FR76 4255 9100 0008 0272 0559 312")
    ),
}


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
    if not emetteur.iban.is_valid:
        raise ValueError(f"L'IBAN émetteur n'est pas valide : {emetteur.iban}.")

    missing_labels = [
        v.beneficiaire.label or v.beneficiaire.nom
        for v in virements
        if not v.description
    ]

    if missing_labels:
        missing_labels = ",".join(f"« {b} »" for b in missing_labels)
        raise ValueError(
            f"Les virements pour les bénéficiaires suivants n'ont pas de libellé : {missing_labels}."
        )

    missing_full_names = [
        v.beneficiaire.label or v.beneficiaire.nom
        for v in virements
        if not v.beneficiaire.nom
    ]

    if missing_full_names:
        missing_full_names = ",".join(f"« {b} »" for b in missing_full_names)
        raise ValidationError(
            f"Les bénéficiaires suivants n'ont pas de nom : {missing_full_names}."
        )

    invalid_ibans = [
        v.beneficiaire for v in virements if not v.beneficiaire.iban.is_valid
    ]

    if invalid_ibans:
        invalid_ibans = ",".join(f"« {b.nom}:{b.iban} »" for b in invalid_ibans)
        raise ValidationError(
            f"Les IBAN des bénéficiaires suivants sont invalides : {invalid_ibans}."
        )

    fichier_sepa = SepaTransfer(
        {
            "name": emetteur.nom,
            "IBAN": str(emetteur.iban),
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
                "IBAN": str(virement.beneficiaire.iban),
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


def validate_bank_transfer_recipients(recipients):
    invalid_ibans = [
        i for i, p in enumerate(recipients) if not p.iban or not p.iban.is_valid
    ]

    if invalid_ibans:
        base_message = ngettext(
            "L'IBAN suivant n'est pas valide :",
            f"{len(invalid_ibans)} IBAN ne sont pas valides :",
            len(invalid_ibans),
        )
        message = "\n".join(
            f"{i + 1}: {recipients[i].iban or '—'} [{recipients[i].label or recipients[i].nom}]"
            for i in invalid_ibans
        )

        raise ValueError(f"{base_message}\n{message}")

    missing_bics = [i for i, p in enumerate(recipients) if not p.bic and not p.iban.bic]

    if missing_bics:
        base_message = ngettext(
            "Le BIC n'est pas connu pour l'IBAN suivant :",
            f"Les BIC ne sont pas connus pour les {len(missing_bics)} IBAN suivants :",
            len(missing_bics),
        )
        message = "\n".join(
            f"{ i + 1 }: {recipients[i].iban} [{recipients[i].label or recipients[i].nom}]"
            for i in missing_bics
        )
        raise ValueError(f"{base_message}\n{message}")


def virements_depuis_dataframe(
    df, *, iban, nom, description, montant, bic=None, date_execution=None
):
    if date_execution is None:
        date_execution = date.today()

    recipients = [
        Partie(
            nom=r[nom],
            iban=IBAN(r[iban]),
            bic=r[bic] if bic and r[bic] and not pd.isna(r[bic]) else None,
        )
        for _, r in df.iterrows()
    ]

    validate_bank_transfer_recipients(recipients)

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


def spending_requests_to_bank_transfers(spending_requests, date_execution=None):
    if date_execution is None:
        date_execution = date.today()

    invalid_status_requests = [
        (i, spending_request)
        for i, spending_request in enumerate(spending_requests)
        if spending_request.status != spending_request.Status.TO_PAY
    ]

    if invalid_status_requests:
        base_message = ngettext(
            "La demande suivante n'est pas indiquée comme « à payer » :",
            f"Les {len(invalid_status_requests)} demandes suivante ne sont pas indiquées comme « à payer » :",
            len(invalid_status_requests),
        )
        message = "\n".join(
            f"{i + 1}: {spending_request.title}"
            for i, spending_request in invalid_status_requests
        )

        raise ValueError(f"{base_message}\n{message}")

    recipients = [
        Partie(
            nom=spending_request.bank_account_full_name.upper(),
            iban=spending_request.bank_account_iban,
            bic=spending_request.bank_account_bic.upper(),
            label=spending_request.title,
        )
        for spending_request in spending_requests
    ]

    validate_bank_transfer_recipients(recipients)

    virements = [
        Virement(
            beneficiaire=recipient,
            montant=spending_request.amount,
            date_execution=date_execution,
            description=spending_request.bank_transfer_label,
        )
        for recipient, spending_request in zip(recipients, spending_requests)
    ]

    return virements
