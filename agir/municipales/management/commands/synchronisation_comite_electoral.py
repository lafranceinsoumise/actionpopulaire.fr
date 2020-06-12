import pandas as pd
from django.core.management import BaseCommand

from agir.municipales.models import CommunePage


class Command(BaseCommand):
    help = "Met à jour les listes que l'on soutient"

    def add_arguments(self, parser):
        parser.add_argument("source")

    def handle(self, *args, source, **options):
        df = self.get_reference_file(source)

        all_communes = {
            c.code: c for c in CommunePage.objects.filter(code__in=df.index)
        }

        liste = df["Nom de la liste 2nd tour"]
        liste = liste.where(df["published"], "")

        tete_liste = df["Tête de liste"].fillna("")

        for commune, liste, tete_liste, published in zip(
            df.index, liste, tete_liste, df.published
        ):
            commune = all_communes.get(commune)
            if commune:
                commune.liste_tour_2 = liste
                commune.tete_liste_tour_2 = tete_liste
                commune.published = published

                commune.save(
                    update_fields=["liste_tour_2", "tete_liste_2", "published",]
                )

    @staticmethod
    def get_reference_file(source):
        df = pd.read_csv(source, dtype={"Code commune": str})

        df["published"] = (
            df["Décision publication"].str.strip().str.lower() == "oui"
        ).fillna(False)

        return df.set_index(df["Code commune"])
