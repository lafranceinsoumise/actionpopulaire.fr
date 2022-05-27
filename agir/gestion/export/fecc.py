from operator import neg
from typing import Iterable

import pandas as pd
from django.db.models import QuerySet
from glom import glom, Val, T, M, Coalesce

from agir.gestion.export import LIBELLES_MODE, lien_document, autres_pieces
from agir.gestion.models import Reglement
from agir.gestion.typologies import TypeDepense
from agir.lib.admin.utils import get_admin_link


def numero(reglement):
    return f"{reglement.numero:05d}{reglement.numero_complement}"


spec_fec = {
    "JournalCode": Val("CCO"),
    "JournalLib": Val("Journal principal"),
    "EcritureNum": numero,
    "EcritureDate": ("created", T.date()),
    "CompteNum": ("numero_compte"),
    "CompteLib": ("depense.type", TypeDepense, T.label),
    "PieceRef": Coalesce("facture.numero", default=""),
    "PieceDate": Coalesce("facture.date", default=""),
    "EcritureLib": "intitule",
    "Debit": ("montant", (M > 0.0) | Val(0.0)),
    "Credit": ("montant", (M < 0.0) | Val(0.0), neg),
    "EcritureLet": Val(""),
    "DateLet": Val(""),
    "ValidDate": "date_validation",
    "Montantdevise": Val(""),
    "Idevise": Val(""),
    "DateRglt": "date_releve",
    "ModeRglt": ("mode", LIBELLES_MODE.get),
    "NatOp": Val(""),
    "DateEvenement": Coalesce(
        ("depense.projet.event.start_time", T.date()), default=None
    ),
    "InseeCode": "code_insee",
    "Libre": Val(""),
    "Type": "depense.nature",
    "DateDébut": "depense.date_debut",
    "DateFin": "depense.date_fin",
    "Quantité": "depense.quantite",
    "LienRèglement": (get_admin_link,),
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
