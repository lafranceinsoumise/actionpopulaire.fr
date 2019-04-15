import json
from pathlib import Path
from unittest.mock import patch, Mock

from functools import wraps

from django.test import TestCase

from agir.lib.geo import geocode_ban
from agir.lib.models import LocationMixin
from agir.people.models import Person


JSON_DIR = Path(__file__).parent / "geoban_json"


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


# test ville normale (une municipalite, pas d'arrondissement)
# test ville pure avec arrondissement
# test arrondissement
# test multi code postale
# test dom/tom
# test invalide poste_code
# test


class BanTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_person(
            "multi_city@test.com", location_country="FR"
        )

    @with_json_response("21570_shared_postcode.json")
    def test_geocode_ban_only_zip(self):
        """
            On a une requette avec de multiple municipalité. On ne peut pas determiner de citycode
        :return:
        """

        self.person.location_zip = "21570"
        self.person.save()

        geocode_ban(self.person)
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

        geocode_ban(self.person)
        self.assertEqual(self.person.location_citycode, "92002")
        self.assertIsNotNone(self.person.coordinates)
        self.assertEqual(self.person.coordinates_type, LocationMixin.COORDINATES_EXACT)

    @with_json_response("21000_dijon.json")
    def test_geocode_ban_only_zip_one_result(self):
        """
            Test le fonctionement avec seulement un code postale mais un seul resultat de commune
        :return:
        """
        self.person.location_zip = "21000"
        self.person.save()

        geocode_ban(self.person)
        self.assert_(self.person.location_citycode, "21231")
        self.assertIsNotNone(self.person.coordinates)
        self.assert_(self.person.coordinates_type, LocationMixin.COORDINATES_EXACT)

    def test_geocode_ban_district_post_code(self):
        """
            Test le fonctionement avec les arrondissement des grande ville qui ont un code INSEE pour chaque arrondissement
        :return:
        """
        self.person.location_zip = "13005"
        self.person.save()

        geocode_ban(self.person)
        self.assertEqual(self.person.location_citycode, "13205")
        self.assertIsNotNone(self.person.coordinates)
        self.assertEqual(
            self.person.coordinates_type, LocationMixin.COORDINATES_DISTRICT
        )

    @with_json_response("45621_invalide.json")
    def test_geocode_ban_invalide_postcode(self):
        """
            Test le fonctionement avec un seulement un code postale invalide
        :return:
        """
        self.person.location_zip = "45621"
        geocode_ban(self.person)
        self.assertIsNone(self.person.coordinates)
        self.assertEqual(
            self.person.coordinates_type, LocationMixin.COORDINATES_NOT_FOUND
        )
