from unittest.mock import patch

from data_france.models import (
    Region,
    Departement,
    Commune,
    CirconscriptionConsulaire,
    CodePostal,
)
from data_france.utils import TypeNom
from django.contrib.gis.geos import Point
from django.test import TestCase
from faker import Faker

from agir.people.models import Person
from agir.voting_proxies.actions import (
    get_voting_proxy_requests_for_proxy,
    match_available_proxies_with_requests,
    find_voting_proxy_candidates_for_requests,
    PER_VOTING_PROXY_REQUEST_INVITATION_LIMIT,
)
from agir.voting_proxies.models import (
    VotingProxy,
    VotingProxyRequest,
)

fake = Faker("fr_FR")


def mock_upcoming_request_queryset(qs):
    return qs


class GetVotingProxyRequestsForProxyTestCase(TestCase):
    def tearDown(self):
        self.patcher.stop()

    def setUp(self):
        self.patcher = patch(
            "agir.voting_proxies.models.VotingProxyRequestQuerySet.upcoming",
            return_value=VotingProxyRequest.objects.all(),
        )
        self.patcher.start()
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
        self.available_date = VotingProxy.VOTING_DATE_CHOICES[0][0]
        self.another_available_date = VotingProxy.VOTING_DATE_CHOICES[3][0]
        self.unavailable_date = VotingProxy.VOTING_DATE_CHOICES[1][0]
        self.accepted_date = VotingProxy.VOTING_DATE_CHOICES[2][0]

        self.voting_proxy = VotingProxy.objects.create(
            **{
                "first_name": "Voting",
                "last_name": "Proxy",
                "email": "voting@proxy.com",
                "contact_phone": "+33600000000",
                "commune": self.commune,
                "polling_station_number": "123",
                "voting_dates": [
                    self.available_date,
                    self.another_available_date,
                    self.accepted_date,
                ],
                "remarks": "R.A.S.",
                "date_of_birth": "1970-01-01",
            }
        )

        self.available_matching_request = VotingProxyRequest.objects.create(
            **{
                "first_name": "a",
                "last_name": "Voter",
                "email": "a_voter@agir.local",
                "contact_phone": "+33600000000",
                "commune": self.commune,
                "consulate": None,
                "polling_station_number": "123",
                "voting_date": self.available_date,
            }
        )
        self.another_available_matching_request = VotingProxyRequest.objects.create(
            **{
                "first_name": "a",
                "last_name": "Voter",
                "email": "a_voter@agir.local",
                "contact_phone": "+33600000000",
                "commune": self.commune,
                "consulate": None,
                "polling_station_number": "123",
                "voting_date": self.another_available_date,
            }
        )
        self.secondary_matching_request = VotingProxyRequest.objects.create(
            **{
                "first_name": "another",
                "last_name": "Voter",
                "email": "another_voter@agir.local",
                "contact_phone": "+33600000000",
                "commune": self.commune,
                "consulate": None,
                "polling_station_number": "123",
                "voting_date": self.another_available_date,
            }
        )
        self.accepted_matching_request = VotingProxyRequest.objects.create(
            **{
                "first_name": "a",
                "last_name": "Voter",
                "email": "accepted_matching@agir.local",
                "contact_phone": "+33600000000",
                "commune": self.commune,
                "consulate": None,
                "polling_station_number": "123",
                "voting_date": self.accepted_date,
                "status": VotingProxyRequest.STATUS_ACCEPTED,
                "proxy": self.voting_proxy,
            }
        )
        self.unmatching_location_request = VotingProxyRequest.objects.create(
            **{
                "first_name": "a",
                "last_name": "Voter",
                "email": "unmatching_location@agir.local",
                "contact_phone": "+33600000000",
                "consulate": self.consulate,
                "polling_station_number": "123",
                "voting_date": self.available_date,
            }
        )
        self.unmatching_date_request = VotingProxyRequest.objects.create(
            **{
                "first_name": "a",
                "last_name": "Voter",
                "email": "unmatching_date@agir.local",
                "contact_phone": "+33600000000",
                "commune": self.commune,
                "polling_station_number": "123",
                "voting_date": self.unavailable_date,
            }
        )

    def test_can_retrieve_matching_requests_for_proxy(self):
        requests = get_voting_proxy_requests_for_proxy(self.voting_proxy, [])
        self.assertFalse(requests.filter(id=self.accepted_matching_request.id).exists())
        self.assertFalse(
            requests.filter(id=self.unmatching_location_request.id).exists()
        )
        self.assertFalse(requests.filter(id=self.unmatching_date_request.id).exists())
        self.assertFalse(
            requests.filter(id=self.secondary_matching_request.id).exists()
        )
        self.assertTrue(requests.filter(id=self.available_matching_request.id).exists())
        self.assertTrue(
            requests.filter(id=self.another_available_matching_request.id).exists()
        )

    def test_can_retrieve_matching_requests_for_proxy_filtered_by_pk(self):
        requests = get_voting_proxy_requests_for_proxy(
            self.voting_proxy, [self.secondary_matching_request.pk]
        )
        self.assertFalse(requests.filter(id=self.accepted_matching_request.id).exists())
        self.assertFalse(
            requests.filter(id=self.unmatching_location_request.id).exists()
        )
        self.assertFalse(requests.filter(id=self.unmatching_date_request.id).exists())
        self.assertFalse(
            requests.filter(id=self.available_matching_request.id).exists()
        )
        self.assertFalse(
            requests.filter(id=self.another_available_matching_request.id).exists()
        )
        self.assertTrue(requests.filter(id=self.secondary_matching_request.id).exists())

    def test_cannot_retrieve_accepted_matching_requests(self):
        with self.assertRaises(VotingProxyRequest.DoesNotExist):
            get_voting_proxy_requests_for_proxy(
                self.voting_proxy, [self.accepted_matching_request.pk]
            )

    def test_cannot_retrieve_unmatching_location_request_requests(self):
        with self.assertRaises(VotingProxyRequest.DoesNotExist):
            get_voting_proxy_requests_for_proxy(
                self.voting_proxy, [self.unmatching_location_request.pk]
            )

    def test_cannot_retrieve_unmatching_date_request_requests(self):
        with self.assertRaises(VotingProxyRequest.DoesNotExist):
            get_voting_proxy_requests_for_proxy(
                self.voting_proxy, [self.unmatching_date_request.pk]
            )


class MatchAvailableProxiesWithRequestsTestCase(TestCase):
    def tearDown(self):
        self.patcher.stop()

    def setUp(self):
        self.patcher = patch(
            "agir.voting_proxies.models.VotingProxyRequestQuerySet.upcoming",
            return_value=VotingProxyRequest.objects.all(),
        )
        self.patcher.start()
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
        self.available_date = VotingProxy.VOTING_DATE_CHOICES[0][0]
        self.another_available_date = VotingProxy.VOTING_DATE_CHOICES[3][0]

    def create_proxy(self, **kwargs):
        email = fake.email()
        person = kwargs.pop("person", None)
        if not person:
            person = Person.objects.create_person(
                email=kwargs.get("email", email),
                create_role=True,
                is_active=True,
            )
        return VotingProxy.objects.create(
            **{
                "first_name": "Voting",
                "last_name": "Proxy",
                "email": email,
                "contact_phone": "+33600000000",
                "commune": None,
                "consulate": self.consulate,
                "polling_station_number": "123",
                "voting_dates": [self.available_date],
                "remarks": "R.A.S.",
                "date_of_birth": "1970-01-01",
                "person": person,
                **kwargs,
            }
        )

    def create_request(self, **kwargs):
        return VotingProxyRequest.objects.create(
            **{
                "first_name": "a",
                "last_name": "Voter",
                "email": "a_voter@agir.local",
                "contact_phone": "+33600000000",
                "commune": None,
                "consulate": self.consulate,
                "polling_station_number": "123",
                "voting_date": self.available_date,
                **kwargs,
            }
        )

    @patch("agir.voting_proxies.actions.send_matching_requests_to_proxy")
    def test_cannot_match_own_request(self, notify_proxy):
        proxy = self.create_proxy()
        request = self.create_request(email=proxy.email)
        qs = VotingProxyRequest.objects.filter(pk=request.pk)
        notify_proxy.assert_not_called()
        fulfilled = match_available_proxies_with_requests(qs, notify_proxy)
        notify_proxy.assert_not_called()
        self.assertEqual(len(fulfilled), 0)

    @patch("agir.voting_proxies.actions.send_matching_requests_to_proxy")
    def test_cannot_match_if_account_is_disabled(self, notify_proxy):
        proxy_person = Person.objects.create_person(
            "disabled_person@proxy.com", create_role=True, is_active=False
        )
        proxy = self.create_proxy(
            email="disabled_person@proxy.com", person=proxy_person
        )
        self.assertFalse(proxy.person.role.is_active)
        request = self.create_request()
        qs = VotingProxyRequest.objects.filter(pk=request.pk)
        notify_proxy.assert_not_called()
        fulfilled = match_available_proxies_with_requests(qs, notify_proxy)
        notify_proxy.assert_not_called()
        self.assertEqual(len(fulfilled), 0)

    @patch("agir.voting_proxies.actions.send_matching_requests_to_proxy")
    def test_cannot_match_proxy_with_unavailable_statuses(self, notify_proxy):
        self.create_proxy(email="invited@proxy.com", status=VotingProxy.STATUS_INVITED)
        self.create_proxy(
            email="unavailable@proxy.com", status=VotingProxy.STATUS_UNAVAILABLE
        )
        request = self.create_request()
        qs = VotingProxyRequest.objects.filter(pk=request.pk)
        notify_proxy.assert_not_called()
        fulfilled = match_available_proxies_with_requests(qs, notify_proxy)
        notify_proxy.assert_not_called()
        self.assertEqual(len(fulfilled), 0)

    @patch("agir.voting_proxies.actions.send_matching_requests_to_proxy")
    def test_cannot_match_the_same_request_multiple_times(self, notify_proxy):
        proxy = self.create_proxy(email="a_proxy@proxy.com")
        another_proxy = self.create_proxy(email="another_proxy@proxy.com")
        request = self.create_request()
        qs = VotingProxyRequest.objects.filter(pk=request.pk)
        notify_proxy.assert_not_called()
        fulfilled = match_available_proxies_with_requests(qs, notify_proxy)
        notify_proxy.assert_called()
        self.assertEqual(len(fulfilled), 1)

    @patch("agir.voting_proxies.actions.send_matching_requests_to_proxy")
    def test_matchings_takes_the_proxy_with_the_most_available_dates_first(
        self, notify_proxy
    ):
        another_proxy = self.create_proxy(
            email="another_proxy@proxy.com", voting_dates=[self.available_date]
        )
        yet_another_proxy = self.create_proxy(
            email="yet_another_proxy@proxy.com",
            voting_dates=[self.another_available_date],
        )
        the_right_proxy = self.create_proxy(
            email="the_right_proxy@proxy.com",
            voting_dates=[self.available_date, self.another_available_date],
        )

        a_request = self.create_request(
            email="voter@agir.test", voting_date=self.available_date
        )
        another_request = self.create_request(
            email="voter@agir.test", voting_date=self.another_available_date
        )

        qs = VotingProxyRequest.objects.filter(
            pk__in=(a_request.pk, another_request.pk)
        )
        notify_proxy.assert_not_called()
        fulfilled = match_available_proxies_with_requests(qs, notify_proxy)
        notify_proxy.assert_called()
        self.assertEqual(len(fulfilled), 2)
        self.assertEqual(notify_proxy.call_args[0][0].pk, the_right_proxy.pk)


class FindVotingProxyCandidatesForRequestsTestCase(TestCase):
    def tearDown(self):
        self.patcher.stop()

    def setUp(self):
        self.patcher = patch(
            "agir.voting_proxies.models.VotingProxyRequestQuerySet.upcoming",
            return_value=VotingProxyRequest.objects.all(),
        )
        self.patcher.start()
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
        self.loc_commune = Commune.objects.create(
            id=1,
            code="00001",
            type=Commune.TYPE_COMMUNE,
            nom="Commune ABC",
            type_nom=TypeNom.ARTICLE_LA,
            departement=dep,
            mairie_localisation=Point(4.92007112503, 46.151676178),
        )
        self.unloc_commune = Commune.objects.create(
            id=2,
            code="00002",
            type=Commune.TYPE_COMMUNE,
            nom="Commune ABC",
            type_nom=TypeNom.ARTICLE_LA,
            departement=dep,
            mairie_localisation=None,
        )
        self.code_postal = CodePostal.objects.create(code="12345")
        self.code_postal.communes.add(self.unloc_commune)
        self.code_postal.save()
        self.country = "PT"
        self.consulate = CirconscriptionConsulaire.objects.create(
            nom="Circonscription Consulaire ABC",
            consulats=["Consulat"],
            nombre_conseillers=1,
            pays=[self.country],
        )
        self.available_date = VotingProxy.VOTING_DATE_CHOICES[0][0]
        self.another_available_date = VotingProxy.VOTING_DATE_CHOICES[3][0]

    def create_proxy(self, **kwargs):
        return VotingProxy.objects.create(
            **{
                "first_name": "Voting",
                "last_name": "Proxy",
                "email": "voting@proxy.com",
                "contact_phone": "+33600000000",
                "commune": None,
                "consulate": self.consulate,
                "polling_station_number": "123",
                "voting_dates": [self.available_date],
                "remarks": "R.A.S.",
                "date_of_birth": "1970-01-01",
                **kwargs,
            }
        )

    def create_request(self, **kwargs):
        return VotingProxyRequest.objects.create(
            **{
                "first_name": "a",
                "last_name": "Voter",
                "email": "a_voter@agir.local",
                "contact_phone": "+33600000000",
                "commune": None,
                "consulate": self.consulate,
                "polling_station_number": "123",
                "voting_date": self.available_date,
                **kwargs,
            }
        )

    def create_proxy_candidate(self, **kwargs):
        return Person.objects.create_political_supporter(
            **{
                "first_name": "a",
                "last_name": "Candidate",
                "email": "a_candidate@agir.local",
                "contact_phone": "+33600000000",
                "location_country": self.country,
                "is_political_support": True,
                **kwargs,
            }
        )

    @patch("agir.voting_proxies.actions.invite_voting_proxy_candidates")
    def test_cannot_invite_to_own_request(self, send_invitations):
        candidate = self.create_proxy_candidate()
        request = self.create_request(email=candidate.email)
        qs = VotingProxyRequest.objects.filter(pk=request.pk)
        send_invitations.assert_not_called()
        (fulfilled, candidates) = find_voting_proxy_candidates_for_requests(
            qs, send_invitations
        )
        send_invitations.assert_not_called()
        self.assertEqual(len(fulfilled), 0)
        self.assertEqual(len(candidates), 0)

    @patch("agir.voting_proxies.actions.invite_voting_proxy_candidates")
    def test_cannot_invite_if_account_is_disabled(self, send_invitations):
        candidate = self.create_proxy_candidate(create_role=True, is_active=False)
        request = self.create_request(email="vpr@agir.test")
        qs = VotingProxyRequest.objects.filter(pk=request.pk)
        send_invitations.assert_not_called()
        (fulfilled, candidates) = find_voting_proxy_candidates_for_requests(
            qs, send_invitations
        )
        send_invitations.assert_not_called()
        self.assertEqual(len(fulfilled), 0)
        self.assertEqual(len(candidates), 0)

    @patch("agir.voting_proxies.actions.invite_voting_proxy_candidates")
    def test_cannot_invite_person_with_no_email(self, send_invitations):
        candidate = self.create_proxy_candidate(email=None)
        request = self.create_request()
        qs = VotingProxyRequest.objects.filter(pk=request.pk)
        send_invitations.assert_not_called()
        (fulfilled, candidates) = find_voting_proxy_candidates_for_requests(
            qs, send_invitations
        )
        send_invitations.assert_not_called()
        self.assertEqual(len(fulfilled), 0)
        self.assertEqual(len(candidates), 0)

    @patch("agir.voting_proxies.actions.invite_voting_proxy_candidates")
    def test_cannot_invite_not_political_support_person(self, send_invitations):
        candidate = self.create_proxy_candidate(is_political_support=False)
        request = self.create_request()
        qs = VotingProxyRequest.objects.filter(pk=request.pk)
        send_invitations.assert_not_called()
        (fulfilled, candidates) = find_voting_proxy_candidates_for_requests(
            qs, send_invitations
        )
        send_invitations.assert_not_called()
        self.assertEqual(len(fulfilled), 0)
        self.assertEqual(len(candidates), 0)

    @patch("agir.voting_proxies.actions.invite_voting_proxy_candidates")
    def test_cannot_invite_person_with_no_newsletters(self, send_invitations):
        candidate = self.create_proxy_candidate(newsletters=[])
        request = self.create_request()
        qs = VotingProxyRequest.objects.filter(pk=request.pk)
        send_invitations.assert_not_called()
        (fulfilled, candidates) = find_voting_proxy_candidates_for_requests(
            qs, send_invitations
        )
        send_invitations.assert_not_called()
        self.assertEqual(len(fulfilled), 0)
        self.assertEqual(len(candidates), 0)

    @patch("agir.voting_proxies.actions.invite_voting_proxy_candidates")
    def test_can_invite_person_with_consulate_country(self, send_invitations):
        candidate = self.create_proxy_candidate(location_country=self.consulate.pays[0])
        request = self.create_request(consulate=self.consulate)
        qs = VotingProxyRequest.objects.filter(pk=request.pk)
        send_invitations.return_value = [candidate.id]
        send_invitations.assert_not_called()
        (fulfilled, candidates) = find_voting_proxy_candidates_for_requests(
            qs, send_invitations
        )
        send_invitations.assert_called_once()
        self.assertEqual(len(fulfilled), 1)
        self.assertEqual(len(candidates), 1)

    @patch("agir.voting_proxies.actions.invite_voting_proxy_candidates")
    def test_can_invite_person_with_commune_coordinates(self, send_invitations):
        candidate = self.create_proxy_candidate(
            coordinates=self.loc_commune.mairie_localisation
        )
        request = self.create_request(consulate=None, commune=self.loc_commune)
        qs = VotingProxyRequest.objects.filter(pk=request.pk)
        send_invitations.return_value = [candidate.id]
        send_invitations.assert_not_called()
        (fulfilled, candidates) = find_voting_proxy_candidates_for_requests(
            qs, send_invitations
        )
        send_invitations.assert_called_once()
        self.assertEqual(len(fulfilled), 1)
        self.assertEqual(len(candidates), 1)

    @patch("agir.voting_proxies.actions.invite_voting_proxy_candidates")
    def test_can_invite_person_with_commune_code(self, send_invitations):
        candidate = self.create_proxy_candidate(
            location_citycode=self.unloc_commune.code
        )
        request = self.create_request(consulate=None, commune=self.unloc_commune)
        qs = VotingProxyRequest.objects.filter(pk=request.pk)
        send_invitations.return_value = [candidate.id]
        send_invitations.assert_not_called()
        (fulfilled, candidates) = find_voting_proxy_candidates_for_requests(
            qs, send_invitations
        )
        send_invitations.assert_called_once()
        self.assertEqual(len(fulfilled), 1)
        self.assertEqual(len(candidates), 1)

    @patch("agir.voting_proxies.actions.invite_voting_proxy_candidates")
    def test_can_invite_person_with_commune_zip_code(self, send_invitations):
        candidate = self.create_proxy_candidate(location_zip=self.code_postal.code)
        request = self.create_request(consulate=None, commune=self.unloc_commune)
        qs = VotingProxyRequest.objects.filter(pk=request.pk)
        send_invitations.return_value = [candidate.id]
        send_invitations.assert_not_called()
        (fulfilled, candidates) = find_voting_proxy_candidates_for_requests(
            qs, send_invitations
        )
        send_invitations.assert_called_once()
        self.assertEqual(len(fulfilled), 1)
        self.assertEqual(len(candidates), 1)

    @patch(
        "agir.voting_proxies.actions.invite_voting_proxy_candidates",
    )
    def test_can_only_invite_n_people_per_request(self, send_invitations):
        candidates = [
            self.create_proxy_candidate(
                email=f"{i}@agir.test", location_zip=self.code_postal.code
            )
            for i in range(PER_VOTING_PROXY_REQUEST_INVITATION_LIMIT + 10)
        ]
        request = self.create_request(consulate=None, commune=self.unloc_commune)
        qs = VotingProxyRequest.objects.filter(pk=request.pk)
        send_invitations.spec = lambda cs: [c.id for c in cs]
        send_invitations.assert_not_called()
        (fulfilled, candidates) = find_voting_proxy_candidates_for_requests(
            qs, send_invitations
        )
        send_invitations.assert_called_once()
        self.assertEqual(
            len(send_invitations.call_args[0][0]),
            PER_VOTING_PROXY_REQUEST_INVITATION_LIMIT,
        )
        self.assertEqual(len(fulfilled), 1)

    @patch(
        "agir.voting_proxies.actions.invite_voting_proxy_candidates",
    )
    def test_invitations_are_sent_for_all_requests(self, send_invitations):
        another_country = "IT"
        another_consulate = CirconscriptionConsulaire.objects.create(
            nom="Circonscription Consulaire DEF",
            consulats=["Consulat"],
            nombre_conseillers=1,
            pays=[another_country],
        )
        a_candidate = self.create_proxy_candidate(
            email="a_candidate@agir.test", location_country=self.country
        )
        another_candidate = self.create_proxy_candidate(
            email="another_candidate@agir.test", location_country=another_country
        )
        a_request = self.create_request(consulate=self.consulate, commune=None)
        another_request = self.create_request(
            email="another_voter@agir.test", consulate=another_consulate, commune=None
        )
        qs = VotingProxyRequest.objects.filter(
            pk__in=[a_request.pk, another_request.pk]
        )
        send_invitations.spec = lambda cs: [c.id for c in cs]
        send_invitations.assert_not_called()
        (fulfilled, candidates) = find_voting_proxy_candidates_for_requests(
            qs, send_invitations
        )
        self.assertEqual(len(fulfilled), 2)
