import uuid
from unittest.mock import patch

from data_france.models import CirconscriptionConsulaire
from django.test import TestCase

from agir.voting_proxies.models import VotingProxyRequest, VotingProxy
from agir.voting_proxies.tasks import (
    send_voting_proxy_request_confirmation,
    send_voting_proxy_request_accepted_text_messages,
    send_voting_proxy_information_for_request,
    send_voting_proxy_request_confirmed_text_messages,
)


class SendVotingProxyRequestConfirmationTestCase(TestCase):
    def tearDown(self):
        self.patcher.stop()

    def setUp(self):
        self.patcher = patch(
            "agir.voting_proxies.models.VotingProxyRequestQuerySet.upcoming",
            return_value=VotingProxyRequest.objects.all(),
        )
        self.patcher.start()
        self.consulate = CirconscriptionConsulaire.objects.create(
            nom="Circonscription Consulaire ABC",
            consulats=["Consulat"],
            nombre_conseillers=1,
        )

        self.voting_proxy_request = VotingProxyRequest.objects.create(
            **{
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "jane_doe@agir.local",
                "contact_phone": "+33600000000",
                "consulate": self.consulate,
                "polling_station_number": "123",
                "voting_date": VotingProxyRequest.VOTING_DATE_CHOICES[0][0],
            }
        )
        self.another_voting_proxy_request = VotingProxyRequest.objects.create(
            **{
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "jane_doe@agir.local",
                "contact_phone": "+33600000000",
                "consulate": self.consulate,
                "polling_station_number": "123",
                "voting_date": VotingProxyRequest.VOTING_DATE_CHOICES[1][0],
            }
        )

    def test_should_raise_exception_if_request_does_not_exist(self):
        unexisting_request_id = uuid.uuid4()
        with self.assertRaises(VotingProxyRequest.DoesNotExist):
            send_voting_proxy_request_confirmation([unexisting_request_id])

    @patch("agir.voting_proxies.tasks.send_sms_message", autospec=True)
    def test_should_send_a_text_message(self, send_sms_message):
        send_sms_message.assert_not_called()
        send_voting_proxy_request_confirmation(
            [self.voting_proxy_request.pk, self.another_voting_proxy_request.pk]
        )
        send_sms_message.assert_called_once()
        self.assertEqual(
            send_sms_message.call_args[0][1], self.voting_proxy_request.contact_phone
        )


class SendVotingProxyRequestAcceptedTextMessagesTestCase(TestCase):
    def tearDown(self):
        self.patcher.stop()

    def setUp(self):
        self.patcher = patch(
            "agir.voting_proxies.models.VotingProxyRequestQuerySet.upcoming",
            return_value=VotingProxyRequest.objects.all(),
        )
        self.patcher.start()
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
                "contact_phone": "+33600000001",
                "consulate": self.consulate,
                "polling_station_number": "123",
                "voting_dates": [VotingProxy.VOTING_DATE_CHOICES[0][0]],
                "remarks": "R.A.S.",
                "date_of_birth": "1970-01-01",
            }
        )

        self.voting_proxy_request = VotingProxyRequest.objects.create(
            **{
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "jane_doe@agir.local",
                "contact_phone": "+33600000000",
                "consulate": self.consulate,
                "polling_station_number": "123",
                "voting_date": VotingProxyRequest.VOTING_DATE_CHOICES[0][0],
                "status": VotingProxyRequest.STATUS_ACCEPTED,
                "proxy": self.voting_proxy,
            }
        )

    def test_should_raise_exception_if_request_does_not_exist(self):
        unexisting_request_id = uuid.uuid4()
        with self.assertRaises(VotingProxyRequest.DoesNotExist):
            send_voting_proxy_request_accepted_text_messages([unexisting_request_id])

    @patch("agir.voting_proxies.tasks.send_sms_message")
    @patch("agir.voting_proxies.tasks.shorten_url")
    def test_should_send_a_text_message(self, shorten_url, send_sms_message):
        shorten_url.return_value = "https://m2022.fr/short_url/"
        send_sms_message.assert_not_called()

        send_voting_proxy_request_accepted_text_messages([self.voting_proxy_request.pk])

        send_sms_message.assert_called()

        self.assertIn(
            self.voting_proxy.first_name, send_sms_message.call_args_list[0].args[0]
        )
        self.assertEqual(
            send_sms_message.call_args_list[0].args[1],
            self.voting_proxy_request.contact_phone,
        )

        self.assertIn(
            self.voting_proxy_request.first_name,
            send_sms_message.call_args_list[1].args[0],
        )
        self.assertEqual(
            send_sms_message.call_args_list[1].args[1], self.voting_proxy.contact_phone
        )


class SendVotingProxyInformationForRequestTestCase(TestCase):
    def tearDown(self):
        self.patcher.stop()

    def setUp(self):
        self.patcher = patch(
            "agir.voting_proxies.models.VotingProxyRequestQuerySet.upcoming",
            return_value=VotingProxyRequest.objects.all(),
        )
        self.patcher.start()
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
                "contact_phone": "+33600000001",
                "consulate": self.consulate,
                "polling_station_number": "123",
                "voting_dates": [VotingProxy.VOTING_DATE_CHOICES[0][0]],
                "remarks": "R.A.S.",
                "date_of_birth": "1970-01-01",
            }
        )

        self.voting_proxy_request = VotingProxyRequest.objects.create(
            **{
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "jane_doe@agir.local",
                "contact_phone": "+33600000000",
                "consulate": self.consulate,
                "polling_station_number": "123",
                "voting_date": VotingProxyRequest.VOTING_DATE_CHOICES[0][0],
                "status": VotingProxyRequest.STATUS_ACCEPTED,
                "proxy": self.voting_proxy,
            }
        )
        self.voting_proxy.refresh_from_db()

    def test_should_raise_exception_if_request_does_not_exist(self):
        unexisting_request_id = uuid.uuid4()
        with self.assertRaises(VotingProxyRequest.DoesNotExist):
            send_voting_proxy_information_for_request(unexisting_request_id)

    @patch("agir.voting_proxies.tasks.send_sms_message")
    def test_should_send_a_text_message(self, send_sms_message):
        send_sms_message.assert_not_called()
        send_voting_proxy_information_for_request(self.voting_proxy_request.pk)
        send_sms_message.assert_called_once()
        self.assertIn(self.voting_proxy.first_name, send_sms_message.call_args[0][0])
        self.assertIn(
            self.voting_proxy.last_name.upper(), send_sms_message.call_args[0][0]
        )
        self.assertIn(
            self.voting_proxy.date_of_birth.strftime("%d/%m/%Y"),
            send_sms_message.call_args[0][0],
        )
        self.assertIn(self.voting_proxy.contact_phone, send_sms_message.call_args[0][0])
        self.assertIn(self.voting_proxy.remarks, send_sms_message.call_args[0][0])
        self.assertEqual(
            send_sms_message.call_args[0][1], self.voting_proxy_request.contact_phone
        )


class SendVotingProxyRequestConfirmedTextMessagesTestCase(TestCase):
    def tearDown(self):
        self.patcher.stop()

    def setUp(self):
        self.patcher = patch(
            "agir.voting_proxies.models.VotingProxyRequestQuerySet.upcoming",
            return_value=VotingProxyRequest.objects.all(),
        )
        self.patcher.start()
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
                "contact_phone": "+33600000001",
                "consulate": self.consulate,
                "polling_station_number": "123",
                "voting_dates": [VotingProxy.VOTING_DATE_CHOICES[0][0]],
                "remarks": "R.A.S.",
                "date_of_birth": "1970-01-01",
            }
        )

        self.voting_proxy_request = VotingProxyRequest.objects.create(
            **{
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "jane_doe@agir.local",
                "contact_phone": "+33600000000",
                "consulate": self.consulate,
                "polling_station_number": "123",
                "voting_date": VotingProxyRequest.VOTING_DATE_CHOICES[0][0],
                "status": VotingProxyRequest.STATUS_ACCEPTED,
                "proxy": self.voting_proxy,
            }
        )
        self.voting_proxy.refresh_from_db()

    def test_should_raise_exception_if_request_does_not_exist(self):
        unexisting_request_id = uuid.uuid4()
        with self.assertRaises(VotingProxyRequest.DoesNotExist):
            send_voting_proxy_request_confirmed_text_messages([unexisting_request_id])

    @patch("agir.voting_proxies.tasks.send_sms_message")
    def test_should_send_a_text_message(self, send_sms_message):
        send_sms_message.assert_not_called()
        send_voting_proxy_request_confirmed_text_messages(
            [self.voting_proxy_request.pk]
        )
        send_sms_message.assert_called_once()
        self.assertIn(
            self.voting_proxy_request.first_name, send_sms_message.call_args[0][0]
        )
        self.assertIn(
            self.voting_proxy_request.last_name.upper(),
            send_sms_message.call_args[0][0],
        )
        self.assertIn(
            self.voting_proxy_request.polling_station_number,
            send_sms_message.call_args[0][0],
        )
        self.assertIn(
            self.voting_proxy_request.contact_phone, send_sms_message.call_args[0][0]
        )
        self.assertEqual(
            send_sms_message.call_args[0][1], self.voting_proxy.contact_phone
        )
