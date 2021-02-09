import json
from pathlib import Path
from unittest.mock import patch, Mock

import requests
from data_france.models import Commune, Departement, Region, CodePostal
from data_france.typologies import TypeNom
from django.contrib.gis.geos import MultiPolygon, Polygon
from django.db import transaction
from django.db.transaction import get_connection
from functools import wraps

from django.test import TestCase

from agir.lib.geo import geocode_france
from agir.lib.models import LocationMixin
from agir.people.models import Person


JSON_DIR = Path(__file__).parent / "geoban_json"
DATA_DIR = Path(__file__).parent / "data"


def import_communes_test_data():

    with transaction.atomic():
        reg = Region.objects.create(
            code="01", nom="Région", type_nom=TypeNom.ARTICLE_LA, chef_lieu_id=1,
        )
        dep = Departement.objects.create(
            code="01",
            nom="Département",
            type_nom=TypeNom.ARTICLE_LE,
            region=reg,
            chef_lieu_id=1,
        )
        c1 = Commune.objects.create(
            id=1,
            code="00001",
            type=Commune.TYPE_COMMUNE,
            nom="Première",
            type_nom=TypeNom.ARTICLE_LA,
            geometry=MultiPolygon(Polygon(((0, 0), (0, 1), (1, 1), (1, 0), (0, 0)))),
            departement=dep,
        )
        c2 = Commune.objects.create(
            id=2,
            code="00002",
            type=Commune.TYPE_COMMUNE,
            nom="Seconde",
            type_nom=TypeNom.ARTICLE_LA,
            geometry=MultiPolygon(Polygon(((0, 0), (0, -1), (1, -1), (1, 0), (0, 0)))),
            departement=dep,
        )
        c3 = Commune.objects.create(
            id=3,
            code="00003",
            type=Commune.TYPE_COMMUNE,
            nom="Troisième",
            type_nom=TypeNom.ARTICLE_LA,
            geometry=MultiPolygon(
                Polygon(((0, 0), (0, -1), (-1, -1), (-1, 0), (0, 0)))
            ),
            departement=dep,
        )
        arr1 = Commune.objects.create(
            id=4,
            code="10001",
            type=Commune.TYPE_ARRONDISSEMENT_PLM,
            nom="Arrondissement",
            type_nom=TypeNom.VOYELLE,
            commune_parent=c1,
            geometry=MultiPolygon(
                Polygon(((0, 0), (0, 0.5), (1, 0.5), (1, 0), (0, 0)))
            ),
        )

        cp1 = CodePostal.objects.create(code="12345")
        cp2 = CodePostal.objects.create(code="54321")
        cp3 = CodePostal.objects.create(code="12300")

        cp1.communes.set([c1])
        cp2.communes.set([c2, c3])
        cp3.communes.set([arr1])


def with_json_response(file_name):
    def wrapper_maker(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with patch("agir.lib.geo.requests") as requests:
                res = requests.get.return_value = Mock()
                with open(JSON_DIR / file_name) as file:
                    res.json.return_value = json.load(file)
                func(*args, **kwargs)

        return wrapper

    return wrapper_maker


def with_no_request(f=None):
    def wrapper_maker(func):
        def wrapper(*args, **kwargs):
            with patch("agir.lib.geo.requests") as requests_patch:
                res = requests_patch.get.side_effect = requests.ConnectionError
                func(*args, **kwargs)

        return wrapper

    if f is not None:
        return wrapper_maker(f)
    return wrapper_maker


class FranceGeocodingTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_insoumise(
            "multi_city@test.com", location_country="FR"
        )
        import_communes_test_data()

    @with_no_request
    def test_geocode_only_zip(self):
        """
            On a une requête avec de multiples municipalités. On ne peut pas determiner de citycode
        :return:
        """

        self.person.location_zip = "54321"
        self.person.save()

        geocode_france(self.person)
        self.assertEqual(self.person.location_citycode, "")
        self.assertIsNotNone(self.person.coordinates)
        self.assertEqual(
            self.person.coordinates_type, LocationMixin.COORDINATES_UNKNOWN_PRECISION
        )

    @with_json_response("92160_adresse_complette.json")
    def test_geocode_ban_complete_address(self):
        """
            Test le fonctionnement avec une adresse complète
        :return:
        """
        self.person.location_address1 = "14 rue du lavoir de la grande pierre"
        self.person.location_city = "Antony"
        self.person.location_zip = "92160"
        self.person.save()

        geocode_france(self.person)
        self.assertEqual(self.person.location_citycode, "92002")
        self.assertIsNotNone(self.person.coordinates)
        self.assertEqual(self.person.coordinates_type, LocationMixin.COORDINATES_EXACT)

    @with_no_request
    def test_geocode_only_zip_one_result(self):
        """
            Test le fonctionement avec seulement un code postale mais un seul resultat de commune
        :return:
        """
        self.person.location_zip = "12345"
        self.person.save()

        geocode_france(self.person)
        self.assert_(self.person.location_citycode, "00001")
        self.assertIsNotNone(self.person.coordinates)
        self.assert_(self.person.coordinates_type, LocationMixin.COORDINATES_CITY)

    @with_no_request
    def test_geocode_ban_district_post_code(self):
        """
            Test le fonctionement avec les arrondissement des grande ville qui ont un code INSEE pour chaque arrondissement
        :return:
        """
        self.person.location_zip = "12300"
        self.person.save()

        geocode_france(self.person)
        self.assertEqual(self.person.location_citycode, "10001")
        self.assertIsNotNone(self.person.coordinates)
        self.assertEqual(
            self.person.coordinates_type, LocationMixin.COORDINATES_DISTRICT
        )

    @with_no_request
    def test_geocode_invalide_postcode(self):
        """
            Test le fonctionement avec un seulement un code postale invalide
        :return:
        """
        self.person.location_zip = "45621"
        self.person.save()
        geocode_france(self.person)
        self.assertIsNone(self.person.coordinates)
        self.assertEqual(
            self.person.coordinates_type, LocationMixin.COORDINATES_NOT_FOUND
        )

    @with_no_request
    def test_geocode_with_citycode(self):

        self.person.location_citycode = "00002"
        self.person.save()
        geocode_france(self.person)

        self.assertIsNotNone(self.person.coordinates)
        self.assertEqual(self.person.coordinates_type, LocationMixin.COORDINATES_CITY)
        self.assertEqual(self.person.location_city, "la Seconde")
