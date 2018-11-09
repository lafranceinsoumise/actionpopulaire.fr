import re
from unittest import mock

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse

from agir.api.redis import using_redislite
from agir.clients.models import Client
from agir.people.models import Person
from agir.people.tasks import send_confirmation_email


class APISubscriptionTestCase(TestCase):
    def setUp(self):
        self.wordpress_client = Client.objects.create_client(
            client_id='wordpress'
        )

        person_content_type = ContentType.objects.get_for_model(Person)
        add_permission = Permission.objects.get(content_type=person_content_type, codename='add_person')
        self.wordpress_client.role.user_permissions.add(add_permission)

    @using_redislite
    @mock.patch("agir.people.serializers.send_confirmation_email")
    def test_can_subscribe_with_api(self, patched_send_confirmation_mail):
        self.client.force_login(self.wordpress_client.role)

        data = {
            'email': 'guillaume@email.com',
            'location_zip': '75004'
        }

        response = self.client.post(
            reverse('legacy:person-subscribe'), data=data,
            HTTP_X_WORDPRESS_CLIENT='192.168.0.1'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        patched_send_confirmation_mail.delay.assert_called_once()
        self.assertEqual(patched_send_confirmation_mail.delay.call_args[1], data)

    def test_cannot_subscribe_without_client_ip(self):
        self.client.force_login(self.wordpress_client.role)

        data = {
            'email': 'guillaume@email.com',
            'location_zip': '75004'
        }

        response = self.client.post(reverse('legacy:person-subscribe'), data=data)

        self.assertEqual(response.status_code, 403)


@using_redislite
class SimpleSubscriptionFormTestCase(TestCase):
    @mock.patch("agir.people.forms.subscription.send_confirmation_email")
    def test_can_subscribe(self, patched_send_confirmation_email):
        data = {'email': 'example@example.com', 'location_zip': '75018'}
        response = self.client.post('/inscription/', data)

        self.assertRedirects(response, reverse('subscription_mail_sent'))

        patched_send_confirmation_email.delay.assert_called_once()
        self.assertEqual(patched_send_confirmation_email.delay.call_args[1], data)

    def test_cannot_subscribe_without_location_zip(self):
        data = {'email': 'example@example.com',}
        response = self.client.post('/inscription/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


@using_redislite
class OverseasSubscriptionTestCase(TestCase):
    @mock.patch("agir.people.forms.subscription.send_confirmation_email")
    def test_can_subscribe(self, patched_send_confirmation_email):
        data = {
            'email': 'example@example.com',
            'location_address1': '1 ZolaStraße',
            'location_address2': '',
            'location_zip': '10178',
            'location_city': 'Berlin',
            'location_country': 'DE'
        }

        response = self.client.post('/inscription/etranger/', data)
        self.assertRedirects(response, reverse('subscription_mail_sent'))

        patched_send_confirmation_email.delay.assert_called_once()
        self.assertEqual(patched_send_confirmation_email.delay.call_args[1], data)


class SubscriptionConfirmationTestCase(TestCase):
    def test_can_receive_mail_and_confirm_subscription(self):
        data = {
            'email': 'guillaume@email.com',
            'location_zip': '75001'
        }

        send_confirmation_email(**data)

        self.assertEqual(len(mail.outbox), 1)

        confirmation_url = reverse('subscription_confirm')
        match = re.search(confirmation_url + r'\?[^" )]+' ,mail.outbox[0].body)

        self.assertIsNotNone(match)
        url_with_params = match.group(0)

        response = self.client.get(url_with_params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertContains(response, 'Bienvenue !')

        # check that the person has been created
        Person.objects.get_by_natural_key('guillaume@email.com')

    def test_can_receive_specific_email_if_already_subscribed(self):
        p = Person.objects.create_person('person@server.fr')

        data = {
            'email': 'person@server.fr',
            'location_zip': '75001',
        }

        send_confirmation_email(**data)

        self.assertEqual(len(mail.outbox), 1)
        self.assertRegex(mail.outbox[0].body, r'vous êtes déjà avec nous !')
