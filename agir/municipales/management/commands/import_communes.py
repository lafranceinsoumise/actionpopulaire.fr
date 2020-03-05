import json

import requests
from django.contrib.gis.geos import MultiPolygon, Polygon, GEOSGeometry
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from functools import reduce
from operator import or_
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

    def polygon_union(self, geoms):
        geoms = [GEOSGeometry(json.dumps(g)) for g in geoms]
        return self.geometry_to_multipolygon(reduce(or_, geoms))

    def geometry_to_multipolygon(self, geom):
        geom = GEOSGeometry(json.dumps(geom))
        if isinstance(geom, Polygon):
            return MultiPolygon(geom)
        elif isinstance(geom, MultiPolygon):
            return geom
        else:
            raise TypeError("Mauvais type de geom (ni polygone ni multipolygone)")

    def handle(self, *args, target, **options):
        if target is None or target == "communes":
            res = requests.get(
                "http://etalab-datasets.geo.data.gouv.fr/contours-administratifs/2019/geojson/communes-5m.geojson"
            )
            data = res.json()
            for feature in tqdm(data["features"]):
                CommunePage.objects.update_or_create(
                    code=feature["properties"]["code"],
                    defaults={
                        "code_departement": feature["properties"]["departement"],
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

            centre = [d["fields"] for d in data["records"] if d["fields"]["c_ar"] <= 4]
            CommunePage.objects.update_or_create(
                code=f"75056SR01",
                defaults={
                    "code_departement": "75",
                    "name": "Paris — centre",
                    "slug": "paris-centre",
                    "coordinates": self.polygon_union([p["geom"] for p in centre]),
                },
            )

            autres = [d["fields"] for d in data["records"] if d["fields"]["c_ar"] > 4]

            for properties in tqdm(autres):
                geom = properties["geom"]

                CommunePage.objects.update_or_create(
                    code=f"75056SR{properties['c_ar']:02d}",
                    defaults={
                        "code_departement": "75",
                        "name": "Paris — {} arrondissement".format(
                            properties["l_ar"].split()[0]
                        ),
                        "slug": "paris-{}{}".format(
                            properties["c_ar"], "e" if properties["c_ar"] != 1 else "er"
                        ),
                        "coordinates": self.geometry_to_multipolygon(geom),
                    },
                )
