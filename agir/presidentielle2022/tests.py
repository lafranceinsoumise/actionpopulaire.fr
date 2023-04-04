from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from rest_framework.test import APITestCase

from agir.groups.models import SupportGroup, Membership
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


class TokTokAPITestCase(APITestCase):
    def setUp(self):
        self.certified_group = SupportGroup.objects.create(
            name="Certified", certification_date=timezone.now()
        )
        self.uncertified_group = SupportGroup.objects.create(
            name="Uncertified", certification_date=None
        )

    def test_anonymous_cannot_access_data(self):
        self.client.logout()
        res = self.client.get("/api/2022/toktok/")
        self.assertEqual(res.status_code, 401)

    def test_person_without_a_group_cannot_access_data(self):
        outcast = Person.objects.create_insoumise("outcast@agir.test", create_role=True)
        self.client.force_login(outcast.role)
        res = self.client.get("/api/2022/toktok/")
        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.data["error"], "not_a_group_member")

    def test_person_without_a_certified_group_cannot_access_data(self):
        misfit = Person.objects.create_insoumise("misfit@agir.test", create_role=True)
        Membership.objects.create(
            supportgroup_id=self.uncertified_group.id,
            person_id=misfit.id,
            membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
        )
        self.client.force_login(misfit.role)
        res = self.client.get("/api/2022/toktok/")
        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.data["error"], "not_a_group_member")

    def test_certified_group_follower_cannot_access_data(self):
        follower = Person.objects.create_insoumise(
            "follower@agir.test", create_role=True
        )
        Membership.objects.create(
            supportgroup_id=self.certified_group.id,
            person_id=follower.id,
            membership_type=Membership.MEMBERSHIP_TYPE_FOLLOWER,
        )
        self.client.force_login(follower.role)
        res = self.client.get("/api/2022/toktok/")
        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.data["error"], "not_a_group_member")

    def test_certified_group_member_can_access_data(self):
        member = Person.objects.create_insoumise("member@agir.test", create_role=True)
        Membership.objects.create(
            supportgroup_id=self.uncertified_group.id,
            person_id=member.id,
            membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
        )
        Membership.objects.create(
            supportgroup_id=self.certified_group.id,
            person_id=member.id,
            membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
        )
        self.client.force_login(member.role)
        res = self.client.get("/api/2022/toktok/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["id"], str(member.id))
        self.assertEqual(res.data["displayName"], member.display_name)
        self.assertEqual(res.data["isManager"], False)
        self.assertEqual(len(res.data["groups"]), 1)
        self.assertEqual(res.data["groups"][0]["id"], self.certified_group.id)

    def test_certified_group_manager_can_access_data(self):
        manager = Person.objects.create_insoumise("manager@agir.test", create_role=True)
        Membership.objects.create(
            supportgroup_id=self.uncertified_group.id,
            person_id=manager.id,
            membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )
        Membership.objects.create(
            supportgroup_id=self.certified_group.id,
            person_id=manager.id,
            membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )
        self.client.force_login(manager.role)
        res = self.client.get("/api/2022/toktok/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["id"], str(manager.id))
        self.assertEqual(res.data["displayName"], manager.display_name)
        self.assertEqual(res.data["isManager"], True)
        self.assertEqual(len(res.data["groups"]), 1)
        self.assertEqual(res.data["groups"][0]["id"], self.certified_group.id)
