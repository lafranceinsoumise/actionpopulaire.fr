from django.contrib.gis.geos import MultiPolygon, Polygon
from django.core.management.base import BaseCommand
import requests
from django.utils.text import slugify
from tqdm import tqdm

from agir.municipales.models import CommunePage


class Command(BaseCommand):
    help = "Met à jour la liste des communes depuis geo.data.gouv.fr"

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            "-c", "--communes", action="store_const", const="communes", dest="target"
        )
        group.add_argument(
            "-p", "--paris", action="store_const", const="paris", dest="target"
        )

    def geometry_to_multipolygon(self, geom):
        if geom["type"] == "Polygon":
            args = (Polygon(*geom["coordinates"]),)
        elif geom["type"] == "MultiPolygon":
            args = (
                Polygon(*polygon_coordinates)
                for polygon_coordinates in geom["coordinates"]
            )
        else:
            raise TypeError("Mauvais type de geom (ni polygone ni multipolygone")
        return MultiPolygon(*args)

    def handle(self, *args, target, **options):
        if target is None or target == "communes":
            res = requests.get(
                "http://etalab-datasets.geo.data.gouv.fr/contours-administratifs/2019/geojson/communes-5m.geojson"
            )
            data = res.json()
            for feature in tqdm(data["features"]):
                CommunePage.objects.update_or_create(
                    code=feature["properties"]["code"],
                    code_departement=feature["properties"]["departement"],
                    defaults={
                        "name": feature["properties"]["nom"],
                        "slug": slugify(feature["properties"]["nom"]),
                        "coordinates": self.geometry_to_multipolygon(
                            feature["geometry"]
                        ),
                    },
                )

        if target is None or target == "paris":
            # arrondissements parisiens
            res = requests.get(
                "https://opendata.paris.fr/api/records/1.0/search/?dataset=arrondissements&rows=20"
            )
            data = res.json()

            for result in tqdm(data["records"]):
                properties = result["fields"]
                geom = properties["geom"]

                CommunePage.objects.update_or_create(
                    code=properties["c_arinsee"],
                    code_departement="75",
                    defaults={
                        "name": "Paris — {} arrondissement".format(
                            properties["l_ar"].split()[0]
                        ),
                        "slug": "paris-{}{}".format(
                            properties["c_ar"], "e" if properties["c_ar"] != 1 else "er"
                        ),
                        "coordinates": self.geometry_to_multipolygon(geom),
                    },
                )
