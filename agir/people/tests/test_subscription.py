import re
from datetime import datetime, timedelta
from unittest import mock
from uuid import uuid4

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse

from agir.api.redis import using_separate_redis_server
from agir.clients.models import Client
from agir.people.models import Person
from agir.people.tasks import send_confirmation_email


class APISubscriptionTestCase(TestCase):
    def setUp(self):
        self.wordpress_client = Client.objects.create_client(client_id="wordpress")

        person_content_type = ContentType.objects.get_for_model(Person)
        add_permission = Permission.objects.get(
            content_type=person_content_type, codename="add_person"
        )
        self.wordpress_client.role.user_permissions.add(add_permission)
        self.client.force_login(self.wordpress_client.role)

    @mock.patch("agir.people.serializers.send_confirmation_email")
    def test_can_subscribe_with_old_api(self, patched_send_confirmation_mail):
        data = {"email": "guillaume@email.com", "location_zip": "75004"}

        response = self.client.post(
            reverse("legacy:person-subscribe"),
            data=data,
            HTTP_X_WORDPRESS_CLIENT="192.168.0.1",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        patched_send_confirmation_mail.delay.assert_called_once()
        self.assertEqual(
            patched_send_confirmation_mail.delay.call_args[1],
            {"location_country": "FR", "type": "LFI", **data},
        )

    @mock.patch("agir.people.serializers.send_confirmation_email")
    def test_can_subscribe_with_new_api(self, send_confirmation_email):
        data = {
            "email": "ragah@fez.com",
            "first_name": "Jim",
            "last_name": "Ballade",
            "location_zip": "75001",
            "contact_phone": "06 98 45 78 45",
            "type": "NSP",
            "referer": str(uuid4()),
        }
        response = self.client.post(reverse("api_people_subscription"), data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        send_confirmation_email.delay.assert_called_once()
        self.assertEqual(
            send_confirmation_email.delay.call_args[1],
            {**data, "location_country": "FR", "contact_phone": "+33698457845"},
        )

    def test_cannot_subscribe_without_client_ip(self):
        data = {"email": "guillaume@email.com", "location_zip": "75004"}

        response = self.client.post(reverse("legacy:person-subscribe"), data=data)

        self.assertEqual(response.status_code, 403)

    @mock.patch("agir.people.serializers.send_confirmation_email")
    def test_can_subscribe_to_new_type_with_existing_person(
        self, send_confirmation_email
    ):
        person = Person.objects.create_insoumise(
            email="type@boite.pays", first_name="Marc", location_zip="75001"
        )

        data = {
            "email": person.email,
            "first_name": "Marco",
            "last_name": "Polo",
            "location_zip": "75004",
            "contact_phone": "",
            "type": "NSP",
        }
        response = self.client.post(reverse("api_people_subscription"), data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        send_confirmation_email.assert_not_called()

        person.refresh_from_db()
        self.assertTrue(person.is_2022)
        self.assertEqual(person.first_name, "Marc")
        self.assertEqual(person.last_name, "Polo")
        self.assertEqual(person.location_zip, "75001")


class SimpleSubscriptionFormTestCase(TestCase):
    @mock.patch("agir.people.forms.subscription.send_confirmation_email")
    def test_can_subscribe(self, patched_send_confirmation_email):
        for zipcode, country_code in [("75018", "FR"), ("97400", "RE")]:
            data = {"email": "example@example.com", "location_zip": zipcode}
            response = self.client.post("/inscription/", data)

            self.assertRedirects(response, reverse("subscription_mail_sent"))

            patched_send_confirmation_email.delay.assert_called_once()
            self.assertEqual(
                patched_send_confirmation_email.delay.call_args[1],
                {"location_country": country_code, **data},
            )
            patched_send_confirmation_email.delay.reset_mock()

    def test_cannot_subscribe_without_location_zip(self):
        data = {"email": "example@example.com"}
        response = self.client.post("/inscription/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_france_country_is_set_by_default(self):
        data = {"email": "my@e.mail", "location_zip": "01337"}

        send_confirmation_email(**data)

        self.assertEqual(len(mail.outbox), 1)

        confirmation_url = reverse("subscription_confirm")
        match = re.search(confirmation_url + r'\?[^" \n)]+', mail.outbox[0].body)

        self.assertIsNotNone(match)
        url_with_params = match.group(0)

        response = self.client.get(url_with_params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertContains(response, "Bienvenue !")

        # check that the person has been created
        person = Person.objects.get_by_natural_key("my@e.mail")

        # check if france is set by default
        self.assertEqual("France", person.location_country.name)


class OverseasSubscriptionTestCase(TestCase):
    @mock.patch("agir.people.forms.subscription.send_confirmation_email")
    def test_can_subscribe(self, patched_send_confirmation_email):
        data = {
            "email": "example@example.com",
            "location_address1": "1 ZolaStraße",
            "location_address2": "",
            "location_zip": "10178",
            "location_city": "Berlin",
            "location_country": "DE",
        }

        response = self.client.post("/inscription/etranger/", data)
        self.assertRedirects(response, reverse("subscription_mail_sent"))

        patched_send_confirmation_email.delay.assert_called_once()
        self.assertEqual(patched_send_confirmation_email.delay.call_args[1], data)


class SubscriptionConfirmationTestCase(TestCase):
    def test_can_receive_mail_and_confirm_subscription(self):
        data = {"email": "guillaume@email.com", "location_zip": "75001"}

        send_confirmation_email(**data)

        self.assertEqual(len(mail.outbox), 1)

        confirmation_url = reverse("subscription_confirm")
        match = re.search(confirmation_url + r'\?[^" \n)]+', mail.outbox[0].body)

        self.assertIsNotNone(match)
        url_with_params = match.group(0)

        response = self.client.get(url_with_params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertContains(response, "Bienvenue !")

        # check that the person has been created
        Person.objects.get_by_natural_key("guillaume@email.com")

    def test_can_receive_specific_email_if_already_subscribed(self):
        p = Person.objects.create_insoumise("person@server.fr")

        data = {"email": "person@server.fr", "location_zip": "75001"}

        send_confirmation_email(**data)

        self.assertEqual(len(mail.outbox), 1)
        self.assertRegex(mail.outbox[0].body, r"vous êtes déjà avec nous !")

    def test_can_subscribe_with_nsp(self):
        data = {
            "email": "personne@organisation.pays",
            "location_zip": "20322",
            "type": "NSP",
        }
        send_confirmation_email(**data)

        self.assertEqual(len(mail.outbox), 1)

        confirmation_url = reverse("subscription_confirm")
        match = re.search(confirmation_url + r'\?[^" \n)]+', mail.outbox[0].body)

        self.assertIsNotNone(match)
        url_with_params = match.group(0)

        response = self.client.get(url_with_params)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        # check that the person has been created
        p = Person.objects.get_by_natural_key("personne@organisation.pays")
        self.assertTrue(p.is_2022)
        self.assertAlmostEqual(
            datetime.fromisoformat(p.meta["subscriptions"]["NSP"]["date"]),
            timezone.now(),
            delta=timedelta(seconds=1),
        )
