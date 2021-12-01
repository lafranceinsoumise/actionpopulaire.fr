import pandas as pd
from data_france.models import Commune
from django.core.management import BaseCommand
from django.utils.text import slugify

from agir.municipales.models import CommunePage


class Command(BaseCommand):
    help = "Met à jour les listes que l'on soutient"

    def add_arguments(self, parser):
        parser.add_argument("source")

    def handle(self, *args, source, **options):
        df = self.get_reference_file(source)

        all_communes = self.get_pages_communes(df.index)

        liste = df["Nom de la liste 2nd tour"]
        liste = liste.where(df["published"] | df["soutenu"], "")
        tete_liste = (
            df["Tête de liste"].where(df["published"] | df["soutenu"]).fillna("")
        )

        for commune, liste, tete_liste, published in zip(
            df.index, liste, tete_liste, df.published
        ):
            commune = all_communes.get(commune)
            if commune:
                commune.liste_tour_2 = liste
                commune.tete_liste_tour_2 = tete_liste
                commune.published = published

                commune.save(
                    update_fields=[
                        "liste_tour_2",
                        "tete_liste_tour_2",
                        "published",
                    ]
                )

        CommunePage.objects.exclude(code__in=df.index).update(
            published=False, liste_tour_2="", tete_liste_tour_2=""
        )

    def get_pages_communes(self, codes):
        pages_commune = {c.code: c for c in CommunePage.objects.filter(code__in=codes)}
        communes_a_creer = set(codes).difference(set(pages_commune))

        for c in communes_a_creer:
            try:
                commune = Commune.objects.get(code=c, type=Commune.TYPE_COMMUNE)
            except Commune.DoesNotExist:
                try:
                    commune = Commune.objects.get(code=c)
                except Commune.DoesNotExist:
                    continue

            pages_commune[c] = CommunePage.objects.create(
                code=commune.code,
                code_departement=commune.code_departement,
                name=commune.nom_complet,
                coordinates=commune.geometry,
                slug=slugify(commune.nom_complet),
            )

        return pages_commune

    @staticmethod
    def get_reference_file(source):
        df = pd.read_csv(source, dtype={"Code commune": str})

        df["published"] = (
            df["Décision publication"].str.strip().str.lower() == "oui"
        ).fillna(False)

        df["soutenu"] = (
            df["Décision soutien"].str.strip().str.lower() == "oui"
        ).fillna(False)

        return df.set_index(df["Code commune"])
