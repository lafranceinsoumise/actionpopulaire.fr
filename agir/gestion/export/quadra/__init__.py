import datetime
from operator import neg
from typing import Iterable, Tuple

import pandas as pd
from django.db.models import QuerySet
from django.utils import timezone
from glom import glom, Val, T, M, Coalesce

from agir.gestion.export import LIBELLES_MODE, lien_document, autres_pieces
from agir.gestion.models import Reglement, Compte
from agir.gestion.typologies import TypeDepense
from agir.lib.admin.utils import get_admin_link


spec_fec = {
    "JournalCode": Val("CCO"),
    "JournalLib": Val("Journal principal"),
    "EcritureNum": "numero",
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
    "LienRèglement": (get_admin_link,),
    "PreuvePaiement": ("preuve", lien_document),
    "LienFacture": ("facture", lien_document),
    "AutresPièces": autres_pieces,
}


def exporter_compte(
    compte: Compte, date_range: Tuple[datetime.date, datetime.date] = None
):
    qs = Reglement.objects.order_by("date").filter(
        depense__compte=compte,
        etat__in=[Reglement.Etat.RAPPROCHE, Reglement.Etat.EXPERTISE],
    )
    if date_range:
        qs = qs.filter(date__range=date_range)

    return exporter_reglements(qs)


def exporter_reglements(
    reglements: Iterable[Reglement] = None,
):
    spec = spec_fec.copy()
    spec["ValidDate"] = Val(timezone.now().date())

    if isinstance(reglements, QuerySet):
        reglements = reglements.select_related(
            "depense__projet__event", "preuve", "facture"
        )

    return pd.DataFrame(glom(reglements, [spec]))
