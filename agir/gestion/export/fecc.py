from operator import neg
from typing import Iterable

import pandas as pd
from django.db.models import QuerySet
from glom import glom, Val, T, M, Coalesce

from agir.gestion.export import (
    LIBELLES_MODE,
    lien_document,
    autres_pieces,
    gestion_admin_link,
    references_pieces,
)
from agir.gestion.models import Reglement
from agir.gestion.typologies import TypeDepense


def numero(reglement):
    return f"{reglement.numero:05d}{reglement.numero_complement}"


compte_num = Coalesce(
    "numero_compte",
    ("depense.type", TypeDepense, T.compte),
    skip=("", None),
    skip_exc=(ValueError,),
    default="",
)

spec_fec = {
    "JournalCode": Val("CCO"),
    "JournalLib": Val("Journal principal"),
    "EcritureNum": numero,
    "EcritureDate": ("created", T.date()),
    "CompteNum": compte_num,
    "CompteLib": (compte_num, TypeDepense.pour_compte, lambda t: t.label if t else ""),
    "PieceRef": references_pieces,
    "PieceDate": Coalesce("facture.date", default=""),
    "EcritureLib": "intitule",
    "Debit": ("montant", (M > 0.0) | Val(0.0)),
    "Credit": ("montant", (M < 0.0) | Val(0.0), neg),
    "EcritureLet": Val(""),
    "DateLet": Val(""),
    "ValidDate": "date_validation",
    "Montantdevise": Val(""),
    "Idevise": Val(""),
    "DateRglt": "date",
    "ModeRglt": ("mode", LIBELLES_MODE.get),
    "NatOp": "depense.nature",
    "DateEvenement": Coalesce(
        "date_evenement",
        "depense.projet.date_evenement",
        ("depense.projet.event.start_time", T.date()),
        default=None,
        skip=(None,),
    ),
    "InseeCode": Coalesce(
        "code_insee",
        "depense.projet.code_insee",
        "depense.projet.event.location_citycode",
        skip=("", None),
        default="00000",
    ),
    "Libre": "libre",
    "_DateDébut": "depense.date_debut",
    "_DateFin": "depense.date_fin",
    "_Quantité": "depense.quantite",
    "_LienRèglement": gestion_admin_link,
    "_PreuvePaiement": ("preuve", lien_document),
    "_LienFacture": ("facture", lien_document),
    "_AutresPièces": autres_pieces,
}


def exporter_reglements(
    reglements: Iterable[Reglement] = None,
    colonnes_supplementaires: bool = True,
):
    if isinstance(reglements, QuerySet):
        reglements = reglements.select_related(
            "depense__projet__event", "preuve", "facture"
        )

    if colonnes_supplementaires:
        spec = spec_fec
    else:
        spec = {k: v for k, v in spec_fec.items() if not k[0] == "_"}

    df = pd.DataFrame(glom(reglements, [spec]))

    if colonnes_supplementaires:
        max_autres_pieces = df["_AutresPièces"].str.len().max()

        autres_colonnes = []

        for i in range(max_autres_pieces):
            df[f"_AutrePièce{i+1}"] = df["_AutresPièces"].str.get(i)
        del df["_AutresPièces"]

    return df
