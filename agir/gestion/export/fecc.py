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
)
from agir.gestion.models import Reglement
from agir.gestion.typologies import TypeDepense


def numero(reglement):
    return f"{reglement.numero:05d}{reglement.numero_complement}"


spec_fec = {
    "JournalCode": Val("CCO"),
    "JournalLib": Val("Journal principal"),
    "EcritureNum": numero,
    "EcritureDate": ("created", T.date()),
    "CompteNum": Coalesce(
        "numero_compte",
        ("depense.type", TypeDepense, T.compte),
        skip=("", None),
        skip_exc=(ValueError,),
        default="",
    ),
    "PieceRef": Coalesce("facture.numero_piece", default=""),
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
    "NatOp": Val(""),
    "DateEvenement": Coalesce(
        ("depense.projet.event.start_time", T.date()), default=None
    ),
    "InseeCode": Coalesce(
        "code_insee",
        "depense.projet.event.location_citycode",
        skip=("", None),
        default="0000",
    ),
    "Libre": "libre",
    "Type": "depense.nature",
    "DateDébut": "depense.date_debut",
    "DateFin": "depense.date_fin",
    "Quantité": "depense.quantite",
    "LienRèglement": gestion_admin_link,
    "PreuvePaiement": ("preuve", lien_document),
    "LienFacture": ("facture", lien_document),
    "AutresPièces": autres_pieces,
}


def exporter_reglements(
    reglements: Iterable[Reglement] = None,
):

    if isinstance(reglements, QuerySet):
        reglements = reglements.select_related(
            "depense__projet__event", "preuve", "facture"
        )

    df = pd.DataFrame(glom(reglements, [spec_fec]))

    max_autres_pieces = df.AutresPièces.str.len().max()

    for i in range(max_autres_pieces):
        df[f"AutrePièce{i+1}"] = df["AutresPièces"].str.get(i)
    del df["AutresPièces"]

    return df
