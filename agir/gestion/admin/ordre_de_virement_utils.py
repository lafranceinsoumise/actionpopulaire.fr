from django.utils import timezone

from agir.gestion.virements import generer_endtoend_id, Virement, Partie
from agir.lib.iban import to_iban

ORDRE_DE_VIREMENT_REQUIRED_COLUMNS = [
    "MONTANT",
    "NOM BENEFICIAIRE",
    "IBAN BENEFICIAIRE",
    "MOTIF",
]


def extract_virements(df):
    virements = []

    for row in df.fillna("").to_dict(orient="records"):
        iban = to_iban(row["IBAN BENEFICIAIRE"])
        beneficiaire = Partie(
            nom=row["NOM BENEFICIAIRE"],
            iban=iban,
            bic=row.get("BIC BENEFICIAIRE") or iban.bic,
        )
        virements.append(
            Virement(
                beneficiaire=beneficiaire,
                montant=round(int(row["MONTANT"]) * 100),
                date_execution=timezone.now().date(),
                description=row["MOTIF"],
                id=generer_endtoend_id(),
            )
        )
    return virements
