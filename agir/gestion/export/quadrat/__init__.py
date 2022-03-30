import datetime
from operator import neg
from typing import Tuple

import pandas as pd
from django.db.models import Subquery, OuterRef
from django.utils import timezone
from glom import glom, Val, T, M, Coalesce

from agir.events.models import Event
from agir.gestion.models import Reglement, Compte
from agir.gestion.typologies import TypeDepense

LIBELLES_MODE = {
    Reglement.Mode.VIREMENT: "VIR",
    Reglement.Mode.PRELEV: "PRLV",
    Reglement.Mode.CHEQUE: "CHQ",
    Reglement.Mode.CARTE: "CB",
    Reglement.Mode.CASH: "ESP",
}


spec_fec = {
    "JournalCode": Val("BQ"),
    "JournalLib": Val("Journal principal"),
    "EcritureNum": Val(""),
    "EcritureDate": "date",
    "CompteNum": ("depense.type", TypeDepense, T.compte),
    "CompteLib": ("depense.type", TypeDepense, T.label),
    "PieceRef": Coalesce("facture.numero", default=""),
    "PieceDate": Coalesce("facture.date", default=""),
    "EcritureLib": "intitule",
    "Debit": ("montant", (M > 0.0) | Val(0.0)),
    "Credit": ("montant", (M < 0.0) | Val(0.0), neg),
    "EcritureLet": Val(""),
    "DateLet": Val(""),
    "ValidDate": Val(""),
    "Montantdevise": Val(""),
    "Idevise": Val(""),
    "DateRglt": "date_releve",
    "ModeRglt": ("mode", LIBELLES_MODE.get),
    "NatOp": Val(""),
    "DateEvenement": Coalesce(
        ("depense.projet.event.start_time", T.date()), default=None
    ),
    "InseeCode": Coalesce("depense.projet.event.location_citycode", default="00000"),
    "Libre": Val(""),
    "Type": "depense.nature",
    "DateDébut": "depense.date_debut",
    "DateFin": "depense.date_fin",
    "Quantité": "depense.quantite",
}


def exporter_compte(
    compte: Compte, date_range: Tuple[datetime.date, datetime.date] = None
):
    spec = spec_fec.copy()
    spec["ValidDate"] = Val(timezone.now().date())

    qs = (
        Reglement.objects.order_by("date")
        .annotate(
            code_insee=Subquery(
                Event.objects.filter(
                    projet__depense__reglement__id=OuterRef("id")
                ).values("location_citycode")[:1]
            ),
        )
        .filter(
            depense__compte=compte,
            etat__in=[Reglement.Etat.RAPPROCHE, Reglement.Etat.EXPERTISE],
        )
        .select_related("depense__projet__event", "preuve", "facture")
    )

    if date_range is not None:
        qs = qs.filter(date__range=date_range)

    qs.update(etat=Reglement.Etat.EXPERTISE)
    return pd.DataFrame(glom(qs, [spec]))
