from django.contrib.gis.geos import MultiPolygon, Polygon
from django.core.management.base import BaseCommand
import requests
from django.utils.text import slugify
from tqdm import tqdm

from agir.municipales.models import CommunePage


class Command(BaseCommand):
    help = "Met à jour la liste des communes depuis geo.data.gouv.fr"

    def handle(self, *args, **options):
        res = requests.get(
            "http://etalab-datasets.geo.data.gouv.fr/contours-administratifs/2019/geojson/communes-5m.geojson"
        )
        data = res.json()
        for feature in tqdm(data["features"]):
            if feature["geometry"]["type"] == "Polygon":
                args = (Polygon(*feature["geometry"]["coordinates"]),)
            if feature["geometry"]["type"] == "MultiPolygon":
                args = (
                    Polygon(*polygon_coordinates)
                    for polygon_coordinates in feature["geometry"]["coordinates"]
                )

            CommunePage.objects.update_or_create(
                code=feature["properties"]["code"],
                code_departement=feature["properties"]["departement"],
                defaults={
                    "name": feature["properties"]["nom"],
                    "slug": slugify(feature["properties"]["nom"]),
                    "coordinates": MultiPolygon(*args),
                },
            )
