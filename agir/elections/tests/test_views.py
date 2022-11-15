from unittest.mock import patch

from data_france.models import (
    Commune,
    CirconscriptionConsulaire,
    Departement,
    Region,
    CirconscriptionLegislative,
)
from data_france.utils import TypeNom
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from agir.elections.models import PollingStationOfficer
from agir.people.models import Person


class PollingStationOfficerCreateAPITestCase(APITestCase):
    def setUp(self):
        ip_bucket_mock = patch(
            "agir.elections.views.create_polling_station_officer_ip_bucket.has_tokens",
            return_value=True,
        )
        ip_bucket_mock.start()
        self.addCleanup(ip_bucket_mock.stop)
        email_bucket_mock = patch(
            "agir.elections.views.create_polling_station_officer_email_bucket.has_tokens",
            return_value=True,
        )
        email_bucket_mock.start()
        self.addCleanup(email_bucket_mock.stop)

        self.create_endpoint = reverse("api_retrieve_create_polling_station_officer")
        self.existing_person = Person.objects.create_person(
            "existing_person@email.com", create_role=True, display_name="Person"
        )
        self.person = Person.objects.create_person(
            "person@email.com", create_role=True, display_name="Person"
        )
        reg = Region.objects.create(
            code="01",
            nom="Région",
            type_nom=TypeNom.ARTICLE_LA,
            chef_lieu_id=1,
        )
        dep = Departement.objects.create(
            code="01",
            nom="Département",
            type_nom=TypeNom.ARTICLE_LE,
            chef_lieu_id=1,
            region=reg,
        )
        self.circo = CirconscriptionLegislative.objects.create(
            code="01-01", departement=dep
        )
        self.circo_abroad = CirconscriptionLegislative.objects.create(code="99-01")
        self.commune = Commune.objects.create(
            id=1,
            code="00001",
            type=Commune.TYPE_COMMUNE,
            nom="Commune ABC",
            type_nom=TypeNom.ARTICLE_LA,
            departement=dep,
        )
        self.consulate = CirconscriptionConsulaire.objects.create(
            nom="Circonscription Consulaire ABC",
            consulats=["Consulat"],
            nombre_conseillers=1,
        )
        self.valid_data = {
            "firstName": "Diane",
            "lastName": "di Prima",
            "gender": PollingStationOfficer.GENDER_FEMALE,
            "birthName": "",
            "birthDate": "1970-01-01",
            "birthCity": "Brooklin",
            "birthCountry": "US",
            "votingCirconscriptionLegislative": self.circo.code,
            "votingCommune": self.commune.id,
            "votingConsulate": None,
            "pollingStation": "1",
            "voterId": "123456789",
            "role": PollingStationOfficer.ROLE_ASSESSEURE_TITULAIRE,
            "availableVotingDates": [PollingStationOfficer.VOTING_DATE_CHOICES[0][0]],
            "address1": "1 rue de la Chine",
            "address2": "",
            "zip": "75019",
            "city": "Paris",
            "country": "FR",
            "email": "dianediprima@agir.local",
            "phone": "+33600000000",
        }

        self.client.force_login(self.person.role)

    def test_can_retrieve_creation_options(self):
        res = self.client.options(self.create_endpoint)
        self.assertEqual(res.status_code, 200)

    def test_cannot_create_without_required_fields(self):
        res = self.client.post(self.create_endpoint, data={})
        self.assertEqual(res.status_code, 422)
        self.assertIn("firstName", res.data)
        self.assertIn("lastName", res.data)
        self.assertIn("gender", res.data)
        self.assertNotIn("birthName", res.data)
        self.assertIn("birthDate", res.data)
        self.assertIn("birthCity", res.data)
        self.assertIn("birthCountry", res.data)
        self.assertIn("pollingStation", res.data)
        self.assertIn("voterId", res.data)
        self.assertIn("role", res.data)
        self.assertIn("availableVotingDates", res.data)
        self.assertIn("address1", res.data)
        self.assertNotIn("address2", res.data)
        self.assertIn("zip", res.data)
        self.assertIn("city", res.data)
        self.assertIn("country", res.data)
        self.assertIn("email", res.data)
        self.assertIn("phone", res.data)
        self.assertIn("votingCirconscriptionLegislative", res.data)

    def test_cannot_create_with_empty_required_fields(self):
        data = {
            "firstName": "",
            "lastName": "",
            "gender": "",
            "birthDate": "",
            "birthCity": "",
            "birthCountry": "",
            "pollingStation": "",
            "voterId": "",
            "role": "",
            "availableVotingDates": [],
            "address1": "",
            "zip": "",
            "city": "",
            "country": "",
            "email": "",
            "phone": "",
            "votingCirconscriptionLegislative": "",
        }
        res = self.client.post(self.create_endpoint, data=data)
        self.assertEqual(res.status_code, 422)
        self.assertIn("firstName", res.data)
        self.assertIn("lastName", res.data)
        self.assertIn("gender", res.data)
        self.assertIn("birthDate", res.data)
        self.assertIn("birthCity", res.data)
        self.assertIn("birthCountry", res.data)
        self.assertIn("pollingStation", res.data)
        self.assertIn("voterId", res.data)
        self.assertIn("role", res.data)
        self.assertIn("availableVotingDates", res.data)
        self.assertIn("address1", res.data)
        self.assertIn("zip", res.data)
        self.assertIn("city", res.data)
        self.assertIn("country", res.data)
        self.assertIn("email", res.data)
        self.assertIn("phone", res.data)
        self.assertIn("votingCirconscriptionLegislative", res.data)

    def test_cannot_create_without_commune_and_consulate(self):
        data = {
            **self.valid_data,
            "votingCommune": None,
            "votingConsulate": None,
        }
        res = self.client.post(self.create_endpoint, data=data)
        self.assertEqual(res.status_code, 422)
        self.assertIn("votingCommune", res.data)
        self.assertIn("votingConsulate", res.data)

    def test_cannot_create_with_both_a_commune_and_a_consulate(self):
        data = {
            **self.valid_data,
            "votingCommune": self.commune.id,
            "votingConsulate": self.consulate.id,
        }
        res = self.client.post(self.create_endpoint, data=data)
        self.assertEqual(res.status_code, 422)
        self.assertIn("votingCommune", res.data)
        self.assertIn("votingConsulate", res.data)

    def test_cannot_create_with_voting_circonscription_and_commune_mismatch(self):
        data = {
            **self.valid_data,
            "votingCommune": self.commune.id,
            "votingConsulate": None,
            "votingCirconscriptionLegislative": self.circo_abroad.code,
        }
        res = self.client.post(self.create_endpoint, data=data)
        self.assertEqual(res.status_code, 422)
        self.assertIn("votingCommune", res.data)

    def test_cannot_create_with_voting_circonscription_and_consulate_mismatch(self):
        data = {
            **self.valid_data,
            "votingCommune": None,
            "votingConsulate": self.consulate.id,
            "votingCirconscriptionLegislative": self.circo.code,
        }
        res = self.client.post(self.create_endpoint, data=data)
        self.assertEqual(res.status_code, 422)
        self.assertIn("votingConsulate", res.data)

    @patch("agir.lib.geo.geocode_element", autospec=True)
    def test_can_create_with_valid_data(self, geocode_france):
        data = {**self.valid_data}
        self.assertEqual(
            PollingStationOfficer.objects.filter(contact_email=data["email"]).count(),
            0,
        )
        self.assertEqual(
            Person.objects.filter(_email=data["email"]).count(),
            0,
        )
        res = self.client.post(self.create_endpoint, data=data)
        self.assertEqual(res.status_code, 201, res.data)
        self.assertFalse(res.data["updated"])
        self.assertEqual(
            PollingStationOfficer.objects.filter(contact_email=data["email"]).count(),
            1,
        )
        self.assertEqual(
            Person.objects.filter(_email=data["email"]).count(),
            1,
        )

    @patch("agir.lib.geo.geocode_element", autospec=True)
    def test_can_update_with_valid_data(self, geocode_france):
        PollingStationOfficer.objects.create(
            **{
                "first_name": self.valid_data["firstName"],
                "last_name": self.valid_data["lastName"],
                "contact_email": self.existing_person.email,
                "contact_phone": self.valid_data["phone"],
                "voting_commune_id": self.valid_data["votingCommune"],
                "polling_station": self.valid_data["pollingStation"],
                "available_voting_dates": self.valid_data["availableVotingDates"],
                "person_id": self.existing_person.id,
                "birth_date": self.valid_data["birthDate"],
                "voting_circonscription_legislative": self.circo,
            }
        )
        data = {**self.valid_data, "email": self.existing_person.email}
        res = self.client.post(self.create_endpoint, data=data)
        self.assertEqual(res.status_code, 201)
        self.assertTrue(res.data["updated"])
        self.assertEqual(
            PollingStationOfficer.objects.filter(contact_email=data["email"]).count(),
            1,
        )
        self.assertEqual(
            Person.objects.filter(_email=data["email"]).count(),
            1,
        )
