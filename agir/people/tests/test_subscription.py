import re
from datetime import datetime, timedelta
from unittest import mock
from unittest.mock import patch

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from agir.clients.models import Client
from agir.lib.http import add_query_params_to_url
from agir.lib.utils import generate_token_params
from agir.people.models import Person, generate_referrer_id
from agir.people.tasks import send_confirmation_email


class WordpressClientMixin:
    def setUp(self):
        self.wordpress_client = Client.objects.create_client(client_id="wordpress")
        self.unauthorized_client = Client.objects.create_client(
            client_id="unauthorized"
        )

        person_content_type = ContentType.objects.get_for_model(Person)
        view_permission = Permission.objects.get(
            content_type=person_content_type, codename="view_person"
        )
        add_permission = Permission.objects.get(
            content_type=person_content_type, codename="add_person"
        )
        change_permission = Permission.objects.get(
            content_type=person_content_type, codename="change_person"
        )

        self.wordpress_client.role.user_permissions.add(
            view_permission, add_permission, change_permission
        )
        self.client.force_login(self.wordpress_client.role)


class APISubscriptionTestCase(WordpressClientMixin, APITestCase):
    @mock.patch("agir.people.serializers.send_confirmation_email")
    def test_can_subscribe_with_new_api(self, send_confirmation_email):
        data = {
            "email": "ragah@fez.com",
            "first_name": "Jim",
            "last_name": "Ballade",
            "location_zip": "75001",
            "contact_phone": "06 98 45 78 45",
            "metadata": {"universite": "Université Paris"},
            "type": "LJI",
            "referrer": generate_referrer_id(),
        }
        response = self.client.post(
            reverse("api_people_subscription"), data=data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        send_confirmation_email.delay.assert_called_once()
        self.assertEqual(
            send_confirmation_email.delay.call_args[1],
            {**data, "location_country": "FR", "contact_phone": "+33698457845"},
        )

    def test_cannot_subscribe_with_new_api_and_unauthorized_client(self):
        self.client.force_login(self.unauthorized_client.role)
        data = {
            "email": "ragah@fez.com",
            "first_name": "Jim",
            "last_name": "Ballade",
            "location_zip": "75001",
            "contact_phone": "06 98 45 78 45",
            "type": "NSP",
            "metadata": {"universite": "Université Paris"},
            "referrer": generate_referrer_id(),
        }
        response = self.client.post(
            reverse("api_people_subscription"), data=data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

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
            "metadata": {"universite": "Université Paris"},
        }
        response = self.client.post(
            reverse("api_people_subscription"), data=data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        send_confirmation_email.assert_not_called()

        person.refresh_from_db()
        self.assertTrue(person.is_political_support)
        self.assertEqual(person.first_name, "Marc")
        self.assertEqual(person.last_name, "Polo")
        self.assertEqual(person.location_zip, "75001")


class SubscriptionConfirmationTestCase(TestCase):
    def setUp(self):
        self.geocode_element = patch("agir.lib.tasks.geocode_element", autospec=True)
        self.geocode_element.start()
        self.addCleanup(self.geocode_element.stop)

    def test_can_receive_mail_and_confirm_subscription(self):
        data = {
            "email": "guillaume@email.com",
            "location_zip": "75001",
            "metadata": {"universite": "Université Paris"},
        }

        send_confirmation_email(**data)

        self.assertEqual(len(mail.outbox), 1)

        confirmation_url = reverse("subscription_confirm")
        match = re.search(confirmation_url + r'\?[^" \n)]+', mail.outbox[0].body)

        self.assertIsNotNone(match)
        url_with_params = match.group(0)

        response = self.client.get(url_with_params)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertTrue(
            response.url.startswith(
                "https://lafranceinsoumise.fr/bienvenue/",
            )
        )

        # check that the person has been created
        Person.objects.get_by_natural_key("guillaume@email.com")

    def test_can_receive_specific_email_if_already_subscribed(self):
        p = Person.objects.create_insoumise("person@server.fr")
        p.ensure_role_exists()

        data = {
            "email": "person@server.fr",
            "location_zip": "75001",
            "metadata": {"universite": "Université Paris"},
        }

        send_confirmation_email(**data)

        self.assertEqual(len(mail.outbox), 1)
        self.assertRegex(mail.outbox[0].body, r"vous êtes déjà avec nous !")

    def test_can_subscribe_with_nsp(self):
        data = {
            "email": "personne@organisation.pays",
            "location_zip": "20322",
            "location_country": "VE",
            "type": "NSP",
        }
        send_confirmation_email(**data)

        self.assertEqual(len(mail.outbox), 1)

        confirmation_url = reverse("subscription_confirm")
        match = re.search(confirmation_url + r'\?[^" \n)]+', mail.outbox[0].body)

        self.assertIsNotNone(match)
        url_with_params = match.group(0)

        avant = timezone.now()
        response = self.client.get(
            url_with_params + "&android=1"
        )  # we add &android=1 cause it should work also in app
        apres = timezone.now()

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        # check that the person has been created
        p = Person.objects.get_by_natural_key("personne@organisation.pays")
        p.ensure_role_exists()

        self.assertTrue(p.is_political_support)
        self.assertEqual(p.location_country, "VE")

        subscription_time = datetime.fromisoformat(
            p.meta["subscriptions"]["NSP"]["date"]
        )

        self.assertTrue(avant <= subscription_time <= apres)

    def test_can_subscribe_with_metadata(self):
        data = {
            "email": "personne@organisation.pays",
            "location_zip": "20322",
            "type": "LJI",
            "metadata": {"universite": "Montaigne", "niveau": "licence"},
        }

        send_confirmation_email(**data)

        self.assertEqual(len(mail.outbox), 1)

        confirmation_url = reverse("subscription_confirm")
        match = re.search(confirmation_url + r'\?[^" \n)]+', mail.outbox[0].body)

        self.assertIsNotNone(match)
        url_with_params = match.group(0)

        avant = timezone.now()
        response = self.client.get(
            url_with_params + "&android=1"
        )  # we add &android=1 cause it should work also in app
        apres = timezone.now()

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        # check that the person has been created
        p = Person.objects.get_by_natural_key("personne@organisation.pays")
        p.ensure_role_exists()

        self.assertTrue(p.is_political_support)
        self.assertEqual(
            p.meta["subscriptions"]["LJI"]["metadata"],
            {"universite": "Montaigne", "niveau": "licence"},
        )


class ManageNewslettersAPIViewTestCase(WordpressClientMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.person = Person.objects.create_person(
            email="a@b.c",
            newsletters=[
                Person.Newsletter.LFI_REGULIERE.value,
                Person.Newsletter.ILB.value,
            ],
            create_role=True,
        )

    def test_can_modify_current_newsletters(self):
        res = self.client.post(
            reverse("api_people_newsletters"),
            data=(
                {
                    "id": str(self.person.id),
                    "newsletters": {
                        Person.Newsletter.LFI_EXCEPTIONNELLE.value: True,
                        Person.Newsletter.ILB.value: False,
                    },
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.person.refresh_from_db()
        self.assertCountEqual(
            self.person.newsletters,
            [
                Person.Newsletter.LFI_REGULIERE.value,
                Person.Newsletter.LFI_EXCEPTIONNELLE.value,
            ],
        )

    def test_cannot_modify_while_anonymous(self):
        self.client.logout()
        res = self.client.post(
            reverse("api_people_newsletters"),
            data=(
                {
                    "id": str(self.person.id),
                    "newsletters": {
                        Person.Newsletter.LFI_EXCEPTIONNELLE.value: True,
                        Person.Newsletter.ILB.value: False,
                    },
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cannot_modify_while_connected_as_same_person(self):
        self.client.force_login(self.person.role)
        res = self.client.post(
            reverse("api_people_newsletters"),
            data=(
                {
                    "id": str(self.person.id),
                    "newsletters": {
                        Person.Newsletter.LFI_EXCEPTIONNELLE.value: True,
                        Person.Newsletter.ILB.value: False,
                    },
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class RetrievePersonAPIViewTestCase(WordpressClientMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.person = Person.objects.create_person(
            email="a@b.c", first_name="A", last_name="B", create_role=True
        )
        self.other_person = Person.objects.create_person(
            email="m@n.o", create_role=True
        )

    def test_can_retrieve_person_information(self):
        res = self.client.get(f"{reverse('api_people_retrieve')}?id={self.person.id}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_can_retrieve_person_information_with_login_link(self):
        self.client.logout()
        params = generate_token_params(self.person)
        url = add_query_params_to_url(
            reverse("api_people_retrieve"),
            {"id": str(self.person.id), "no_session": "o", **params},
        )
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_can_retrieve_while_connected_as_same_person(self):
        self.client.force_login(self.person.role)
        res = self.client.get(f"{reverse('api_people_retrieve')}?id={self.person.id}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_cannot_retrieve_while_connected_as_different_person(self):
        self.client.force_login(self.other_person.role)
        res = self.client.get(f"{reverse('api_people_retrieve')}?id={self.person.id}")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_retrieve_while_anonymous(self):
        self.client.logout()
        res = self.client.get(f"{reverse('api_people_retrieve')}?id={self.person.id}")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
