import pandas as pd
from django.core.management import BaseCommand
from tqdm import tqdm

from agir.municipales.models import CommunePage, Liste

URL = "https://static.data.gouv.fr/resources/elections-municipales-2020-candidatures-au-1er-tour/20200304-105123/livre-des-listes-et-candidats.txt"
DTYPE = {
    "Code du département": "category",
    "Libellé du département": "category",
    "Code commune": str,  # attention aux secteurs de Marseille
    "Nuance Liste": "category",
    "Nationalité": "category",
    "Candidat au conseil communautaire": "category",
    "N° candidat": str,
}


def pairs(it):
    it = iter(it)

    try:
        b = next(it)
        while True:
            a, b = b, next(it)
            yield a, b
    except StopIteration:
        pass


class Command(BaseCommand):
    help = "Importer les listes du ministère pour pouvoir faire les rapprochements avec nos listes."

    def import_listes(self):
        df = pd.read_csv(URL, sep="\t", dtype=DTYPE, skiprows=2, encoding="latin1")

        df.columns = [
            "departement",
            "departement_libelle",
            "commune",
            "commune_libelle",
            "liste_numero",
            "liste_nom_court",
            "liste_nom",
            "nuance",
            "candidat_numero",
            "candidat_sexe",
            "candidat_nom",
            "candidat_prenom",
            "nationalite",
            "conseil_communautaire",
            "excedentaire",
        ]

        # vide, probablement causée par des tabulations excédentaires à la fin des lignes
        del df["excedentaire"]

        # Deux listes où il y a eu un décalage des colonnes vers la droite : on corrige
        fausses_nuances = [
            "LE LARDIN ST LAZARE , un nouveau départ",
            "BATIR AVEC VOUS LE BAS DE DEMAIN",
        ]
        mask = df.nuance.isin(fausses_nuances)

        df.loc[mask, "liste_nom_court"] = (
            df.loc[mask, "liste_nom_court"] + df.loc[mask, "liste_nom"]
        )

        # décalage des colonnes vers la gauche
        for target, src in pairs(
            [
                "liste_nom",
                "nuance",
                "candidat_numero",
                "candidat_sexe",
                "candidat_nom",
                "candidat_prenom",
            ]
        ):
            df.loc[mask, target] = df.loc[mask, src]

        # on a malheureusement pas le prénom du coup
        df.loc[mask, "candidat_prenom"] = pd.NA
        df["candidat_numero"] = df["candidat_numero"].astype(int)

        return df

    def handle(self, *args, **options):
        df = self.import_listes()

        df["insee"] = df["departement"].astype(str).str.zfill(2) + df[
            "commune"
        ].str.zfill(3)

        df["liste_code"] = (
            df["insee"] + "-" + df["liste_numero"].astype(str).str.zfill(2)
        )

        df["conseil_communautaire"] = df["conseil_communautaire"] == "O"

        listes = (
            df[["liste_code", "insee", "liste_nom", "nuance"]]
            .drop_duplicates()
            .set_index(["liste_code"])
        )
        listes["nuance"] = (
            listes["nuance"]
            .cat.remove_unused_categories()
            .cat.add_categories([""])
            .fillna("")
        )
        listes["candidats_noms"] = df.groupby(["liste_code"])["candidat_nom"].agg(list)
        listes["candidats_prenoms"] = df.groupby(["liste_code"])["candidat_prenom"].agg(
            list
        )
        listes["candidats_communautaire"] = df.groupby(["liste_code"])[
            "conseil_communautaire"
        ].agg(list)

        communes_ids = {
            c["code"]: c["id"]
            for c in CommunePage.objects.filter(
                code__in=listes["insee"].unique()
            ).values("id", "code")
        }

        for l in tqdm(listes.itertuples(), total=len(listes)):
            Liste.objects.update_or_create(
                code=l.Index,
                defaults={
                    "nom": l.liste_nom,
                    "nuance": l.nuance,
                    "candidats_noms": l.candidats_noms,
                    "candidats_prenoms": l.candidats_prenoms,
                    "candidats_communautaire": l.candidats_communautaire,
                    "commune_id": communes_ids.get(l.insee),
                },
            )
