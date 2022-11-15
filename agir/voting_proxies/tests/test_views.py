from unittest.mock import patch

from data_france.models import Commune, CirconscriptionConsulaire, Departement, Region
from data_france.utils import TypeNom
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from agir.lib.http import add_query_params_to_url
from agir.people.models import Person
from agir.voting_proxies.models import VotingProxyRequest, VotingProxy


class VotingProxyRequestCreateAPITestCase(APITestCase):
    def setUp(self):
        ip_bucket_mock = patch(
            "agir.voting_proxies.views.create_voter_ip_bucket.has_tokens",
            return_value=True,
        )
        ip_bucket_mock.start()
        self.addCleanup(ip_bucket_mock.stop)
        email_bucket_mock = patch(
            "agir.voting_proxies.views.create_voter_email_bucket.has_tokens",
            return_value=True,
        )
        email_bucket_mock.start()
        self.addCleanup(email_bucket_mock.stop)

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
        self.client.force_login(self.person.role)

    def test_can_retrieve_creation_options(self):
        res = self.client.options(self.create_endpoint)
        self.assertEqual(res.status_code, 200)

    def test_cannot_create_without_required_fields(self):
        res = self.client.post(self.create_endpoint, data={})
        self.assertEqual(res.status_code, 422)
        self.assertIn("firstName", res.data)
        self.assertIn("lastName", res.data)
        self.assertIn("email", res.data)
        self.assertIn("phone", res.data)
        self.assertIn("votingDates", res.data)

    def test_cannot_create_with_empty_required_fields(self):
        data = {
            "firstName": "",
            "lastName": "",
            "email": "",
            "phone": "",
            "commune": None,
            "consulate": None,
            "votingDates": [],
        }
        res = self.client.post(self.create_endpoint, data=data)
        self.assertEqual(res.status_code, 422)
        self.assertIn("firstName", res.data)
        self.assertIn("lastName", res.data)
        self.assertIn("email", res.data)
        self.assertIn("phone", res.data)
        self.assertIn("votingDates", res.data)

    def test_cannot_create_without_commune_and_consulate(self):
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

    @patch("agir.voting_proxies.tasks.send_sms_message", autospec=True)
    def test_can_create_a_request_with_valid_data(self, send_sms_message):
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

    @patch("agir.voting_proxies.tasks.send_sms_message", autospec=True)
    def test_can_update_a_request_with_valid_data_if_one_exists_for_the_email_and_date(
        self, send_sms_message
    ):
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


class VotingProxyCreateAPITestCase(APITestCase):
    def setUp(self):
        VotingProxyRequestQuerySet_upcoming = patch(
            "agir.voting_proxies.models.VotingProxyRequestQuerySet.upcoming",
            return_value=VotingProxyRequest.objects.all(),
        )
        VotingProxyRequestQuerySet_upcoming.start()
        self.addCleanup(VotingProxyRequestQuerySet_upcoming.stop)

        ip_bucket_mock = patch(
            "agir.voting_proxies.views.create_voter_ip_bucket.has_tokens",
            return_value=True,
        )
        ip_bucket_mock.start()
        self.addCleanup(ip_bucket_mock.stop)

        email_bucket_mock = patch(
            "agir.voting_proxies.views.create_voter_email_bucket.has_tokens",
            return_value=True,
        )
        email_bucket_mock.start()
        self.addCleanup(email_bucket_mock.stop)

        geocode_element = patch("agir.lib.tasks.geocode_element", autospec=True)
        geocode_element.start()
        self.addCleanup(geocode_element.stop)

        self.create_endpoint = reverse("api_create_voting_proxy")
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
            "votingDates": [VotingProxy.VOTING_DATE_CHOICES[0][0]],
            "remarks": "R.A.S.",
            "newsletters": [],
            "dateOfBirth": "1970-01-01",
            "address": "25 passage dubail",
            "zip": "75010",
            "city": "Paris",
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
        self.assertIn("email", res.data)
        self.assertIn("phone", res.data)
        self.assertIn("votingDates", res.data)

    def test_cannot_create_with_empty_required_fields(self):
        data = {
            "firstName": "",
            "lastName": "",
            "email": "",
            "phone": "",
            "commune": None,
            "consulate": None,
            "votingDates": [],
            "dateOfBirth": "",
        }
        res = self.client.post(self.create_endpoint, data=data)
        self.assertEqual(res.status_code, 422)
        self.assertIn("firstName", res.data)
        self.assertIn("lastName", res.data)
        self.assertIn("email", res.data)
        self.assertIn("phone", res.data)
        self.assertIn("votingDates", res.data)
        self.assertIn("dateOfBirth", res.data)

    def test_cannot_create_without_commune_and_consulate(self):
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
        data = {
            **self.valid_data,
            "commune": self.commune.id,
            "consulate": self.consulate.id,
        }
        res = self.client.post(self.create_endpoint, data=data)
        self.assertEqual(res.status_code, 422)
        self.assertIn("commune", res.data)
        self.assertIn("consulate", res.data)

    def test_cannot_create_with_a_commune_and_with_empty_address_fields(self):
        data = {
            **self.valid_data,
            "commune": self.commune.id,
            "consulate": None,
            "address": "",
            "zip": "",
            "city": "",
        }
        res = self.client.post(self.create_endpoint, data=data)
        self.assertEqual(res.status_code, 422)
        self.assertIn("address", res.data)
        self.assertIn("zip", res.data)
        self.assertIn("city", res.data)

    @patch("agir.lib.geo.geocode_element", autospec=True)
    def test_can_create_with_valid_data(self, geocode_france):
        data = {**self.valid_data}
        self.assertEqual(
            VotingProxy.objects.filter(email=data["email"]).count(),
            0,
        )
        self.assertEqual(
            Person.objects.filter(_email=data["email"]).count(),
            0,
        )
        res = self.client.post(self.create_endpoint, data=data)
        self.assertEqual(res.status_code, 201)
        self.assertFalse(res.data["updated"])
        self.assertEqual(
            VotingProxy.objects.filter(email=data["email"]).count(),
            1,
        )
        self.assertEqual(
            Person.objects.filter(_email=data["email"]).count(),
            1,
        )

    @patch("agir.lib.geo.geocode_element", autospec=True)
    def test_can_update_with_valid_data(self, geocode_france):
        VotingProxy.objects.create(
            **{
                "first_name": self.valid_data["firstName"],
                "last_name": self.valid_data["lastName"],
                "email": self.existing_person.email,
                "contact_phone": self.valid_data["phone"],
                "commune_id": self.valid_data["commune"],
                "polling_station_number": self.valid_data["pollingStationNumber"],
                "voting_dates": self.valid_data["votingDates"],
                "person": self.existing_person,
                "date_of_birth": "1970-01-01",
            }
        )
        data = {**self.valid_data, "email": self.existing_person.email}
        res = self.client.post(self.create_endpoint, data=data)
        self.assertEqual(res.status_code, 201)
        self.assertTrue(res.data["updated"])
        self.assertEqual(
            VotingProxy.objects.filter(email=data["email"]).count(),
            1,
        )
        self.assertEqual(
            Person.objects.filter(_email=data["email"]).count(),
            1,
        )


class VotingProxyRetrieveUpdateAPITestCase(APITestCase):
    def tearDown(self):
        self.patcher.stop()

    def setUp(self):
        self.patcher = patch(
            "agir.voting_proxies.models.VotingProxyRequestQuerySet.upcoming",
            return_value=VotingProxyRequest.objects.all(),
        )
        self.patcher.start()
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
        self.voting_proxy = VotingProxy.objects.create(
            **{
                "first_name": "Diane",
                "last_name": "di Prima",
                "email": "diane@dianediprima.org",
                "contact_phone": "+33600000000",
                "commune": self.commune,
                "consulate": None,
                "polling_station_number": "123",
                "voting_dates": [VotingProxy.VOTING_DATE_CHOICES[0][0]],
                "remarks": "R.A.S.",
                "person": self.person,
                "date_of_birth": "1970-01-01",
            }
        )
        self.endpoint = reverse(
            "api_retrieve_update_voting_proxy", kwargs={"pk": self.voting_proxy.pk}
        )
        self.client.force_login(self.person.role)

    def test_can_retrieve_voting_proxy(self):
        res = self.client.get(self.endpoint)
        self.assertEqual(res.status_code, 200)
        self.assertIn("email", res.data)

    def test_can_retrieve_update_options(self):
        res = self.client.options(self.endpoint)
        self.assertEqual(res.status_code, 200)

    def test_cannot_create_with_null_commune_and_consulate(self):
        self.assertIsNone(self.voting_proxy.consulate)
        data = {
            "commune": None,
        }
        res = self.client.patch(self.endpoint, data=data)
        self.assertEqual(res.status_code, 422)
        self.assertIn("commune", res.data)
        self.assertIn("consulate", res.data)

    def test_cannot_create_with_both_a_commune_and_a_consulate(self):
        self.assertIsNotNone(self.voting_proxy.commune)
        data = {
            "consulate": self.consulate.id,
        }
        res = self.client.patch(self.endpoint, data=data)
        self.assertEqual(res.status_code, 422)
        self.assertIn("commune", res.data)
        self.assertIn("consulate", res.data)

    def test_cannot_update_the_email_address(self):
        email = self.voting_proxy.email
        data = {"email": "not-" + email}
        self.client.patch(self.endpoint, data=data)
        self.voting_proxy.refresh_from_db(fields=["email"])
        self.assertNotEqual(data["email"], self.voting_proxy.email)
        self.assertEqual(email, self.voting_proxy.email)

    def test_can_update_voting_proxy(self):
        data = {
            "firstName": "Boo",
            "lastName": "Radley",
            "phone": "+33612345678",
            "commune": None,
            "consulate": self.consulate.id,
            "pollingStationNumber": "Polling Office N°25",
            "status": VotingProxy.STATUS_CREATED,
            "votingDates": [str(VotingProxy.VOTING_DATE_CHOICES[0][0])],
            "remarks": "I am vegetarian",
            "dateOfBirth": "1970-01-01",
        }
        res = self.client.patch(self.endpoint, data=data)
        self.assertEqual(res.status_code, 200, res.data)
        self.voting_proxy.refresh_from_db()
        self.assertEqual(self.voting_proxy.first_name, data["firstName"])
        self.assertEqual(self.voting_proxy.last_name, data["lastName"])
        self.assertEqual(self.voting_proxy.contact_phone, data["phone"])
        self.assertEqual(self.voting_proxy.commune_id, data["commune"])
        self.assertEqual(self.voting_proxy.consulate_id, data["consulate"])
        self.assertEqual(
            self.voting_proxy.polling_station_number, data["pollingStationNumber"]
        )
        self.assertEqual(self.voting_proxy.status, data["status"])
        self.assertEqual(self.voting_proxy.voting_dates, data["votingDates"])
        self.assertEqual(self.voting_proxy.remarks, data["remarks"])


class ReplyToVotingProxyRequestsAPITestCase(APITestCase):
    def tearDown(self):
        self.patcher.stop()

    def setUp(self):
        self.patcher = patch(
            "agir.voting_proxies.models.VotingProxyRequestQuerySet.upcoming",
            return_value=VotingProxyRequest.objects.all(),
        )
        self.patcher.start()
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
        self.voting_proxy = VotingProxy.objects.create(
            **{
                "first_name": "Voting",
                "last_name": "Proxy",
                "email": "voting@proxy.com",
                "contact_phone": "+33600000000",
                "commune": self.commune,
                "consulate": None,
                "polling_station_number": "123",
                "voting_dates": [VotingProxy.VOTING_DATE_CHOICES[0][0]],
                "remarks": "R.A.S.",
                "person": self.person,
                "status": VotingProxy.STATUS_CREATED,
                "date_of_birth": "1970-01-01",
            }
        )
        self.another_voting_proxy = VotingProxy.objects.create(
            **{
                "first_name": "Another Voting",
                "last_name": "Proxy",
                "email": "another_voting@proxy.com",
                "contact_phone": "+33600000000",
                "commune": self.commune,
                "consulate": None,
                "polling_station_number": "123",
                "voting_dates": [VotingProxy.VOTING_DATE_CHOICES[0][0]],
                "remarks": "R.A.S.",
                "status": VotingProxy.STATUS_CREATED,
                "date_of_birth": "1970-01-01",
            }
        )
        self.unavailable_voting_proxy = VotingProxy.objects.create(
            **{
                "first_name": "Unavailable Voting",
                "last_name": "Proxy",
                "email": "unavailable_voting@proxy.com",
                "contact_phone": "+33600000000",
                "commune": self.commune,
                "consulate": None,
                "polling_station_number": "123",
                "voting_dates": [VotingProxy.VOTING_DATE_CHOICES[0][0]],
                "remarks": "R.A.S.",
                "status": VotingProxy.STATUS_UNAVAILABLE,
                "date_of_birth": "1970-01-01",
            }
        )
        self.endpoint = reverse(
            "api_reply_to_voting_proxy_requests", kwargs={"pk": self.voting_proxy.pk}
        )
        self.matching_request = VotingProxyRequest.objects.create(
            **{
                "first_name": "A",
                "last_name": "Voter",
                "email": "a_voter@agir.local",
                "contact_phone": "+33600000000",
                "commune": self.commune,
                "consulate": None,
                "polling_station_number": "123",
                "voting_date": VotingProxy.VOTING_DATE_CHOICES[0][0],
            }
        )
        self.unmatching_request = VotingProxyRequest.objects.create(
            **{
                "first_name": "Another",
                "last_name": "Voter",
                "email": "another_votern@agir.local",
                "contact_phone": "+33600000000",
                "commune": self.commune,
                "consulate": None,
                "polling_station_number": "123",
                "voting_date": VotingProxy.VOTING_DATE_CHOICES[1][0],
            }
        )
        self.accepted_request = VotingProxyRequest.objects.create(
            **{
                "first_name": "A third",
                "last_name": "Voter",
                "email": "a_third_voter@agir.local",
                "contact_phone": "+33600000000",
                "commune": self.commune,
                "consulate": None,
                "polling_station_number": "123",
                "voting_date": VotingProxy.VOTING_DATE_CHOICES[0][0],
                "status": VotingProxyRequest.STATUS_ACCEPTED,
                "proxy": self.another_voting_proxy,
            }
        )
        self.client.force_login(self.person.role)

    def test_cannot_retrieve_requests_for_unavailable_proxy(self):
        endpoint = reverse(
            "api_reply_to_voting_proxy_requests",
            kwargs={"pk": self.unavailable_voting_proxy.pk},
        )
        res = self.client.get(endpoint)
        self.assertEqual(res.status_code, 404)

    def test_cannot_retrieve_unmatching_requests(self):
        endpoint = add_query_params_to_url(
            self.endpoint, {"vpr": str(self.unmatching_request.pk)}
        )
        res = self.client.get(endpoint)
        self.assertEqual(res.status_code, 200)
        self.assertIn("requests", res.data)
        self.assertEqual(len(res.data["requests"]), 0)

    def test_cannot_retrieve_accepted_requests(self):
        endpoint = add_query_params_to_url(
            self.endpoint, {"vpr": str(self.accepted_request.pk)}
        )
        res = self.client.get(endpoint)
        self.assertEqual(res.status_code, 200)
        self.assertIn("requests", res.data)
        self.assertEqual(len(res.data["requests"]), 0)

    def test_can_retrieve_available_matching_requests(self):
        res = self.client.get(self.endpoint)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["firstName"], self.voting_proxy.first_name)
        self.assertIn("requests", res.data)
        self.assertEqual(len(res.data["requests"]), 1)
        self.assertEqual(res.data["requests"][0]["id"], self.matching_request.pk)

    def test_can_retrieve_available_matching_requests_filtered_by_pk(self):
        endpoint = add_query_params_to_url(
            self.endpoint, {"vpr": str(self.matching_request.pk)}
        )
        res = self.client.get(endpoint)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["firstName"], self.voting_proxy.first_name)
        self.assertIn("requests", res.data)
        self.assertEqual(len(res.data["requests"]), 1)
        self.assertEqual(res.data["requests"][0]["id"], self.matching_request.pk)

    def test_cannot_update_for_unavailable_proxy(self):
        endpoint = reverse(
            "api_reply_to_voting_proxy_requests",
            kwargs={"pk": self.unavailable_voting_proxy.pk},
        )
        data = {
            "isAvailable": True,
            "votingProxyRequests": [str(self.matching_request.pk)],
        }
        res = self.client.patch(endpoint, data)
        self.assertEqual(res.status_code, 404)

    def test_cannot_update_without_isAvailable_param(self):
        data = {"votingProxyRequests": [str(self.matching_request.pk)]}
        res = self.client.patch(self.endpoint, data=data)
        self.assertEqual(res.status_code, 422)
        self.assertIn("isAvailable", res.data)

    def test_cannot_update_with_invalid_isAvailable_param(self):
        data = {
            "votingProxyRequests": [str(self.matching_request.pk)],
            "isAvailable": "not a boolean",
        }
        res = self.client.patch(self.endpoint, data=data)
        self.assertEqual(res.status_code, 422)
        self.assertIn("isAvailable", res.data)

    def test_cannot_update_without_votingProxyRequests_param(self):
        data = {"isAvailable": True}
        res = self.client.patch(self.endpoint, data=data)
        self.assertEqual(res.status_code, 422)
        self.assertIn("votingProxyRequests", res.data)

    def test_cannot_update_with_empty_votingProxyRequests_param(self):
        data = {
            "votingProxyRequests": [],
            "isAvailable": True,
        }
        res = self.client.patch(self.endpoint, data=data)
        self.assertEqual(res.status_code, 422)
        self.assertIn("votingProxyRequests", res.data)

    def test_cannot_update_with_invalid_votingProxyRequests_param(self):
        data = {
            "votingProxyRequests": ["not a uuid"],
            "isAvailable": True,
        }
        res = self.client.patch(self.endpoint, data=data)
        self.assertEqual(res.status_code, 422)
        self.assertIn("global", res.data)

    def test_cannot_update_with_unmatching_voting_proxy_request(self):
        data = {
            "votingProxyRequests": [str(self.unmatching_request.pk)],
            "isAvailable": True,
        }
        res = self.client.patch(self.endpoint, data=data)
        self.assertEqual(res.status_code, 422)
        self.assertIn("global", res.data)

    def test_cannot_update_with_unavailable_voting_proxy_request(self):
        data = {
            "votingProxyRequests": [str(self.accepted_request.pk)],
            "isAvailable": True,
        }
        res = self.client.patch(self.endpoint, data=data)
        self.assertEqual(res.status_code, 422)
        self.assertIn("global", res.data)

    def test_can_decline_a_request(self):
        self.matching_request.proxy = None
        self.matching_request.status = VotingProxyRequest.STATUS_CREATED
        self.voting_proxy.status = VotingProxy.STATUS_CREATED
        data = {
            "votingProxyRequests": [str(self.matching_request.pk)],
            "isAvailable": False,
        }
        res = self.client.patch(self.endpoint, data=data)
        self.assertEqual(res.status_code, 200)
        self.matching_request.refresh_from_db()
        self.voting_proxy.refresh_from_db()
        self.assertEqual(self.voting_proxy.status, VotingProxy.STATUS_UNAVAILABLE)
        self.assertEqual(self.matching_request.proxy, None)
        self.assertEqual(
            self.matching_request.status, VotingProxyRequest.STATUS_CREATED
        )

    def test_can_accept_a_request(self):
        self.matching_request.proxy = None
        self.matching_request.status = VotingProxyRequest.STATUS_CREATED
        self.voting_proxy.status = VotingProxy.STATUS_CREATED
        data = {
            "votingProxyRequests": [str(self.matching_request.pk)],
            "isAvailable": True,
        }
        res = self.client.patch(self.endpoint, data=data)
        self.assertEqual(res.status_code, 200)
        self.matching_request.refresh_from_db()
        self.assertEqual(self.matching_request.proxy, self.voting_proxy)
        self.assertEqual(
            self.matching_request.status, VotingProxyRequest.STATUS_ACCEPTED
        )
        self.voting_proxy.refresh_from_db(fields=["status"])
        self.assertEqual(self.voting_proxy.status, VotingProxy.STATUS_AVAILABLE)


class VotingProxyForRequestRetrieveAPITestCase(APITestCase):
    def tearDown(self):
        self.patcher.stop()

    def setUp(self):
        self.patcher = patch(
            "agir.voting_proxies.models.VotingProxyRequestQuerySet.upcoming",
            return_value=VotingProxyRequest.objects.all(),
        )
        self.patcher.start()
        self.person = Person.objects.create_person(
            "person@email.com", create_role=True, display_name="Person"
        )
        self.consulate = CirconscriptionConsulaire.objects.create(
            nom="Circonscription Consulaire ABC",
            consulats=["Consulat"],
            nombre_conseillers=1,
        )
        self.voting_proxy = VotingProxy.objects.create(
            **{
                "first_name": "Voting",
                "last_name": "Proxy",
                "email": "voting@proxy.com",
                "contact_phone": "+33600000000",
                "consulate": self.consulate,
                "polling_station_number": "123",
                "voting_dates": [VotingProxy.VOTING_DATE_CHOICES[0][0]],
                "remarks": "R.A.S.",
                "person": self.person,
                "status": VotingProxy.STATUS_CREATED,
                "date_of_birth": "1970-01-01",
            }
        )
        self.unaccepted_request = VotingProxyRequest.objects.create(
            **{
                "first_name": "A",
                "last_name": "Voter",
                "email": "a_voter@agir.local",
                "contact_phone": "+33600000000",
                "consulate": self.consulate,
                "polling_station_number": "123",
                "voting_date": VotingProxy.VOTING_DATE_CHOICES[0][0],
            }
        )
        self.accepted_request = VotingProxyRequest.objects.create(
            **{
                "first_name": "A third",
                "last_name": "Voter",
                "email": "a_third_voter@agir.local",
                "contact_phone": "+33600000000",
                "consulate": self.consulate,
                "polling_station_number": "123",
                "voting_date": VotingProxy.VOTING_DATE_CHOICES[0][0],
                "status": VotingProxyRequest.STATUS_ACCEPTED,
                "proxy": self.voting_proxy,
            }
        )

        self.client.force_login(self.person.role)

    def get_endpoint(self, pk):
        return reverse("api_retrieve_voting_proxy_for_request", kwargs={"pk": pk})

    @patch("agir.voting_proxies.views.send_voting_proxy_information_for_request.delay")
    def test_cannot_receive_information_for_unaccepted_request(
        self, send_voting_proxy_information_for_request
    ):
        send_voting_proxy_information_for_request.assert_not_called()
        endpoint = self.get_endpoint(self.unaccepted_request.pk)
        res = self.client.get(endpoint)
        self.assertEqual(res.status_code, 404)
        send_voting_proxy_information_for_request.assert_not_called()

    @patch("agir.voting_proxies.views.send_voting_proxy_information_for_request.delay")
    def test_can_receive_information_for_accepted_request(
        self, send_voting_proxy_information_for_request
    ):
        send_voting_proxy_information_for_request.assert_not_called()
        endpoint = self.get_endpoint(self.accepted_request.pk)
        res = self.client.get(endpoint)
        self.assertEqual(res.status_code, 202)
        send_voting_proxy_information_for_request.assert_called_once_with(
            self.accepted_request.pk
        )


class VotingProxyRequestConfirmAPITestCase(APITestCase):
    def tearDown(self):
        self.patcher.stop()

    def setUp(self):
        self.patcher = patch(
            "agir.voting_proxies.models.VotingProxyRequestQuerySet.upcoming",
            return_value=VotingProxyRequest.objects.all(),
        )
        self.patcher.start()
        self.person = Person.objects.create_person(
            "person@email.com", create_role=True, display_name="Person"
        )
        self.consulate = CirconscriptionConsulaire.objects.create(
            nom="Circonscription Consulaire ABC",
            consulats=["Consulat"],
            nombre_conseillers=1,
        )
        self.voting_proxy = VotingProxy.objects.create(
            **{
                "first_name": "Voting",
                "last_name": "Proxy",
                "email": "voting@proxy.com",
                "contact_phone": "+33600000000",
                "consulate": self.consulate,
                "polling_station_number": "123",
                "voting_dates": [VotingProxy.VOTING_DATE_CHOICES[0][0]],
                "remarks": "R.A.S.",
                "person": self.person,
                "status": VotingProxy.STATUS_CREATED,
                "date_of_birth": "1970-01-01",
            }
        )
        self.voting_proxy_request = VotingProxyRequest.objects.create(
            **{
                "first_name": "A",
                "last_name": "Voter",
                "email": "a_voter@agir.local",
                "contact_phone": "+33600000000",
                "consulate": self.consulate,
                "polling_station_number": "123",
                "voting_date": VotingProxy.VOTING_DATE_CHOICES[0][0],
                "proxy": self.voting_proxy,
                "status": VotingProxyRequest.STATUS_ACCEPTED,
            }
        )
        self.endpoint = reverse("api_confirm_voting_proxy_request")
        self.client.force_login(self.person.role)

    @patch("agir.voting_proxies.views.confirm_voting_proxy_requests")
    def test_cannot_confirm_an_unaccepted_request(self, confirm_voting_proxy_requests):
        confirm_voting_proxy_requests.assert_not_called()
        self.voting_proxy_request.proxy = self.voting_proxy
        self.voting_proxy_request.status = VotingProxyRequest.STATUS_CANCELLED
        self.voting_proxy_request.save()
        data = {
            "votingProxyRequests": [str(self.voting_proxy_request.pk)],
        }
        res = self.client.patch(self.endpoint, data=data)
        self.assertEqual(res.status_code, 422)
        self.assertIn("votingProxyRequests", res.data)
        self.voting_proxy_request.refresh_from_db()
        self.assertEqual(
            self.voting_proxy_request.status, VotingProxyRequest.STATUS_CANCELLED
        )
        confirm_voting_proxy_requests.assert_not_called()

    @patch("agir.voting_proxies.views.confirm_voting_proxy_requests")
    def test_can_confirm_an_accepted_request(self, confirm_voting_proxy_requests):
        confirm_voting_proxy_requests.assert_not_called()
        self.voting_proxy_request.proxy = self.voting_proxy
        self.voting_proxy_request.status = VotingProxyRequest.STATUS_ACCEPTED
        self.voting_proxy_request.save()
        data = {
            "votingProxyRequests": [str(self.voting_proxy_request.pk)],
        }
        res = self.client.patch(self.endpoint, data=data)
        self.assertEqual(res.status_code, 200)
        self.voting_proxy_request.refresh_from_db()
        confirm_voting_proxy_requests.assert_called_once()
