from datetime import timedelta
from unittest.mock import patch

from data_france.models import Region, Departement, Commune, CirconscriptionConsulaire
from data_france.utils import TypeNom
from django.test import TestCase
from django.utils import timezone

from agir.voting_proxies.actions import (
    get_voting_proxy_requests_for_proxy,
    match_available_proxies_with_requests,
)
from agir.voting_proxies.models import VotingProxy, VotingProxyRequest


class GetVotingProxyRequestsForProxyTestCase(TestCase):
    def setUp(self):
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
    def setUp(self):
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

    @patch("agir.voting_proxies.actions.send_matching_requests_to_proxy")
    def test_cannot_match_own_request(self, notify_proxy):
        proxy = self.create_proxy(email="voting@proxy.com")
        request = self.create_request(email=proxy.email)
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
    def test_cannot_match_proxy_already_matched_less_than_2_days_ago(
        self, notify_proxy
    ):
        self.create_proxy(
            email="matched_proxy@proxy.com",
            status=VotingProxy.STATUS_CREATED,
            last_matched=timezone.now() - timedelta(days=1),
        )
        request = self.create_request()
        qs = VotingProxyRequest.objects.filter(pk=request.pk)
        notify_proxy.assert_not_called()
        fulfilled = match_available_proxies_with_requests(qs, notify_proxy)
        notify_proxy.assert_not_called()
        self.assertEqual(len(fulfilled), 0)

    @patch("agir.voting_proxies.actions.send_matching_requests_to_proxy")
    def test_cannot_match_proxy_who_has_already_replied_to_a_request(
        self, notify_proxy
    ):
        proxy = self.create_proxy(
            email="taken_proxy@proxy.com",
            status=VotingProxy.STATUS_CREATED,
            last_matched=timezone.now() - timedelta(days=1),
        )
        taken_request = self.create_request(
            proxy=proxy, voting_date=self.another_available_date
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
        proxy = self.create_proxy(
            email="a_proxy@proxy.com",
            voting_dates=[self.available_date, self.another_available_date],
        )
        another_proxy = self.create_proxy(
            email="another_proxy@proxy.com", voting_dates=[self.available_date]
        )
        yet_another_proxy = self.create_proxy(
            email="yet_another_proxy@proxy.com",
            voting_dates=[self.another_available_date],
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
        self.assertEqual(notify_proxy.call_args[0][0].pk, proxy.pk)
