from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from faker import Faker

from agir.carte.models import StaticMapImage

fake = Faker("fr_FR")

__all__ = ["CreateStaticMapImageFromJAWG"]


class CreateStaticMapImageFromJAWG(TestCase):
    def setUp(self):
        coords = fake.local_latlng(country_code="FR", coords_only=True)
        self.center = Point(float(coords[1]), float(coords[0]))

    def test_can_download_and_create_static_map_image(self):
        StaticMapImage.objects.create(center=self.center)

    def test_cannot_download_and_create_duplicate(self):
        StaticMapImage.objects.create(center=self.center)
        with self.assertRaises(IntegrityError):
            StaticMapImage.objects.create_from_jawg(center=self.center)

    def test_cannot_download_and_create_without_center(self):
        with self.assertRaises(ValidationError):
            StaticMapImage.objects.create()

    def test_cannot_download_and_create_with_invalid_zoom(self):
        with self.assertRaises(ValidationError):
            StaticMapImage.objects.create(center=self.center, zoom=10000)
