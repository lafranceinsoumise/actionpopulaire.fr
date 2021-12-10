from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APITestCase

from agir.payments.models import Payment, Subscription
from agir.people.models import Person
from agir.presidentielle2022 import (
    AFCPJLMCheckDonationPaymentMode,
    AFCP2022SystemPayPaymentMode,
)
from agir.presidentielle2022.apps import Presidentielle2022Config


class PublicDonationAggregatesAPITestCase(APITestCase):
    def setUp(self):
        self.person = Person.objects.create_insoumise(
            "person@email.com", create_role=True
        )
        self.person.role.user_permissions.add(
            Permission.objects.get(
                content_type=ContentType.objects.get_for_model(Person),
                codename="view_person",
            )
        )
        self.pending_payment = Payment.objects.create(
            person=self.person,
            price=100,
            type=Presidentielle2022Config.DONATION_PAYMENT_TYPE,
            mode=AFCPJLMCheckDonationPaymentMode,
            status=Payment.STATUS_WAITING,
        )
        self.single_donation = Payment.objects.create(
            person=self.person,
            price=100,
            type=Presidentielle2022Config.DONATION_PAYMENT_TYPE,
            mode=AFCPJLMCheckDonationPaymentMode,
            status=Payment.STATUS_COMPLETED,
        )
        self.subscription = Subscription.objects.create(
            person=self.person,
            price=100,
            type=Presidentielle2022Config.DONATION_SUBSCRIPTION_TYPE,
            mode=AFCP2022SystemPayPaymentMode,
            status=Subscription.STATUS_ACTIVE,
        )
        self.monthly_donation = Payment.objects.create(
            person=self.person,
            price=100,
            type=Presidentielle2022Config.DONATION_SUBSCRIPTION_TYPE,
            mode=AFCP2022SystemPayPaymentMode,
            status=Payment.STATUS_COMPLETED,
            subscription=self.subscription,
        )
        self.expected_total_amount = 200

    def test_authenticated_user_can_get_right_donation_amount(self):
        self.client.force_login(self.person.role)
        res = self.client.get("/api/2022/dons/")
        self.assertIn("totalAmount", res.data)
        self.assertEqual(res.data["totalAmount"], self.expected_total_amount)


class DonationAggregatesAPITestCase(APITestCase):
    def setUp(self):
        self.person = Person.objects.create_insoumise(
            "person@email.com", create_role=True
        )
        self.person.role.user_permissions.add(
            Permission.objects.get(
                content_type=ContentType.objects.get_for_model(Person),
                codename="view_person",
            )
        )
        self.pending_payment = Payment.objects.create(
            person=self.person,
            price=100,
            type=Presidentielle2022Config.DONATION_PAYMENT_TYPE,
            mode=AFCPJLMCheckDonationPaymentMode,
            status=Payment.STATUS_WAITING,
        )
        self.single_donation = Payment.objects.create(
            person=self.person,
            price=100,
            type=Presidentielle2022Config.DONATION_PAYMENT_TYPE,
            mode=AFCPJLMCheckDonationPaymentMode,
            status=Payment.STATUS_COMPLETED,
        )
        self.subscription = Subscription.objects.create(
            person=self.person,
            price=100,
            type=Presidentielle2022Config.DONATION_SUBSCRIPTION_TYPE,
            mode=AFCP2022SystemPayPaymentMode,
            status=Subscription.STATUS_ACTIVE,
        )
        self.monthly_donation = Payment.objects.create(
            person=self.person,
            price=100,
            type=Presidentielle2022Config.DONATION_SUBSCRIPTION_TYPE,
            mode=AFCP2022SystemPayPaymentMode,
            status=Payment.STATUS_COMPLETED,
            subscription=self.subscription,
        )
        self.expected_total_amount = 200

    def test_authenticated_user_can_get_right_donation_amount(self):
        self.client.force_login(self.person.role)
        res = self.client.get("/api/2022/dons/")
        self.assertIn("totalAmount", res.data)
        self.assertEqual(res.data["totalAmount"], self.expected_total_amount)
