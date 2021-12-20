from copy import deepcopy

from data_france.models import Commune, CirconscriptionConsulaire, Departement, Region
from data_france.utils import TypeNom
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from agir.people.models import Person
from agir.voting_proxies.models import VotingProxyRequest, VotingProxy


class VotingProxyRequestCreateAPITestCase(APITestCase):
    def setUp(self):
        self.create_endpoint = reverse("api_create_voting_proxy_request")
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
            "email": "diane@dianediprima.org",
            "phone": "0600000000",
            "commune": self.commune.id,
            "consulate": None,
            "pollingStationNumber": "123",
            "votingDates": [VotingProxyRequest.VOTING_DATE_CHOICES[0][0]],
        }

    def test_can_retrieve_creation_options(self):
        self.client.force_login(self.person.role)
        res = self.client.options(self.create_endpoint)
        self.assertEqual(res.status_code, 200)

    def test_cannot_create_without_required_fields(self):
        self.client.force_login(self.person.role)
        res = self.client.post(self.create_endpoint, data={})
        self.assertEqual(res.status_code, 422)
        self.assertIn("firstName", res.data)
        self.assertIn("lastName", res.data)
        self.assertIn("email", res.data)
        self.assertIn("phone", res.data)
        self.assertIn("pollingStationNumber", res.data)
        self.assertIn("votingDates", res.data)

    def test_cannot_create_with_empty_required_fields(self):
        self.client.force_login(self.person.role)
        data = {
            "firstName": "",
            "lastName": "",
            "email": "",
            "phone": "",
            "commune": None,
            "consulate": None,
            "pollingStationNumber": "",
            "votingDates": [],
        }
        res = self.client.post(self.create_endpoint, data=data)
        self.assertEqual(res.status_code, 422)
        self.assertIn("firstName", res.data)
        self.assertIn("lastName", res.data)
        self.assertIn("email", res.data)
        self.assertIn("phone", res.data)
        self.assertIn("pollingStationNumber", res.data)
        self.assertIn("votingDates", res.data)

    def test_cannot_create_without_commune_and_consulate(self):
        self.client.force_login(self.person.role)
        data = {
            **self.valid_data,
            "commune": None,
            "consulate": None,
        }
        res = self.client.post(self.create_endpoint, data=data)
        self.assertEqual(res.status_code, 422)
        self.assertIn("commune", res.data)
        self.assertIn("consulate", res.data)

    def test_cannot_create_with_both_a_commune_and_a_consulate(self):
        self.client.force_login(self.person.role)
        data = {
            **self.valid_data,
            "commune": self.commune.id,
            "consulate": self.consulate.id,
        }
        res = self.client.post(self.create_endpoint, data=data)
        self.assertEqual(res.status_code, 422)
        self.assertIn("commune", res.data)
        self.assertIn("consulate", res.data)

    def test_cannot_create_a_request_if_one_exists_for_the_date_and_email_with_a_proxy(
        self,
    ):
        proxy = VotingProxy.objects.create(
            first_name="Foo",
            last_name="Bar",
            email="foo@bar.com",
            contact_phone="+33600000000",
            voting_dates=[VotingProxyRequest.VOTING_DATE_CHOICES[0][0]],
            commune=self.commune,
        )
        request = VotingProxyRequest.objects.create(
            first_name="Bar",
            last_name="Baz",
            email="bar@baz.com",
            contact_phone="+33600000000",
            voting_date=VotingProxyRequest.VOTING_DATE_CHOICES[0][0],
            commune=self.commune,
            proxy=proxy,
        )
        self.client.force_login(self.person.role)
        data = {**self.valid_data, "email": request.email}
        res = self.client.post(self.create_endpoint, data=data)
        self.assertEqual(res.status_code, 422)
        self.assertIn("global", res.data)

    def test_can_create_a_request_with_valid_data(self):
        self.client.force_login(self.person.role)
        data = {**self.valid_data, "email": "email@agir.local"}
        self.assertFalse(
            VotingProxyRequest.objects.filter(
                email="email@agir.local", voting_date=data["votingDates"][0]
            ).exists()
        )
        res = self.client.post(self.create_endpoint, data=data)
        self.assertEqual(res.status_code, 201)
        self.assertFalse(res.data["updated"])
        self.assertTrue(
            VotingProxyRequest.objects.filter(
                email="email@agir.local", voting_date=data["votingDates"][0]
            ).exists()
        )

    def test_can_update_a_request_with_valid_data_if_one_exists_for_the_email_and_date(
        self,
    ):
        self.client.force_login(self.person.role)
        data = {**self.valid_data}
        self.assertEqual(
            VotingProxyRequest.objects.filter(
                email=data["email"],
                voting_date=data["votingDates"][0],
            ).count(),
            0,
        )
        res = self.client.post(self.create_endpoint, data=data)
        self.assertEqual(res.status_code, 201)
        self.assertFalse(res.data["updated"])
        self.assertEqual(
            VotingProxyRequest.objects.filter(
                email=data["email"],
                voting_date=data["votingDates"][0],
            ).count(),
            1,
        )
        res = self.client.post(self.create_endpoint, data=data)
        self.assertEqual(res.status_code, 201)
        self.assertTrue(res.data["updated"])
        self.assertEqual(
            VotingProxyRequest.objects.filter(
                email=data["email"],
                voting_date=data["votingDates"][0],
            ).count(),
            1,
        )
