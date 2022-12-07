import json
import re
import uuid
from functools import partial
from unittest import mock
from urllib.parse import urlencode

from django.conf import settings
from django.core import mail
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from agir.api.redis import using_separate_redis_server
from agir.donations.apps import DonsConfig
from agir.donations.models import Operation, MonthlyAllocation
from agir.donations.tasks import (
    send_monthly_donation_confirmation_email,
    send_donation_email,
)
from agir.groups.models import SupportGroup, Membership, SupportGroupSubtype
from agir.lib.utils import front_url
from agir.payments import payment_modes
from agir.payments.actions.payments import (
    complete_payment,
    create_payment,
    notify_status_change,
)
from agir.payments.actions.subscriptions import complete_subscription
from agir.payments.models import Payment, Subscription
from agir.people.models import Person
from agir.system_pay import SystemPayPaymentMode
from ..views import (
    notification_listener as donation_notification_listener,
    subscription_notification_listener as monthly_donation_subscription_listener,
)
from ... import donations
from ...authentication.tokens import monthly_donation_confirmation_token_generator
from ...system_pay.models import SystemPayAlias, SystemPaySubscription


class DonationTestMixin:
    def setUp(self):
        self.p1 = Person.objects.create_2022("test@test.com", create_role=True)

        self.donation_information_payload = {
            "nationality": "FR",
            "firstName": "Marc",
            "lastName": "Frank",
            "locationAddress1": "4 rue de Chaume",
            "locationAddress2": "",
            "locationZip": "33000",
            "locationCity": "Bordeaux",
            "locationCountry": "FR",
            "contactPhone": "+33645789845",
            "amount": "20000",
            "paymentMode": payment_modes.DEFAULT_MODE,
            "paymentTiming": donations.serializers.SINGLE_TIME,
            "gender": "F",
        }

        certified_subtype = SupportGroupSubtype.objects.create(
            type=SupportGroup.TYPE_LOCAL_GROUP,
            label=settings.CERTIFIED_GROUP_SUBTYPES[0],
        )

        self.group = SupportGroup.objects.create(
            name="Groupe", type=SupportGroup.TYPE_LOCAL_GROUP
        )
        self.group.subtypes.set([certified_subtype])
        Membership.objects.create(
            supportgroup=self.group,
            person=self.p1,
            membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
        )

        self.other_group = SupportGroup.objects.create(
            name="Autre groupe", type=SupportGroup.TYPE_LOCAL_GROUP
        )
        self.other_group.subtypes.set([certified_subtype])
        Membership.objects.create(
            supportgroup=self.other_group,
            person=self.p1,
            membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
        )

        self.amount_url = reverse("donation_amount")
        self.information_modal_url = reverse("donation_information_modal")
        self.create_donation_url = reverse("api_donation_create")


class DonationTestCase(DonationTestMixin, APITestCase):
    @mock.patch("django.db.transaction.on_commit")
    def test_can_donate_while_logged_in(self, on_commit):
        self.client.force_login(self.p1.role)

        res = self.client.get(self.amount_url)
        self.assertEqual(res.status_code, 200)

        res = self.client.get(self.information_modal_url)
        self.assertEqual(res.status_code, 200)

        res = self.client.post(
            self.create_donation_url, self.donation_information_payload
        )
        # no other payment
        payment = Payment.objects.get()
        self.assertEqual(res.status_code, 200)
        self.assertIn(front_url("payment_page", args=(payment.pk,)), res.data["next"])

        self.client.get(reverse("payment_return", args=(payment.pk,)))

        self.p1.refresh_from_db()

        # assert fields have been saved on model
        self.assertEqual(
            self.p1.first_name, self.donation_information_payload["firstName"]
        )
        self.assertEqual(
            self.p1.last_name, self.donation_information_payload["lastName"]
        )
        self.assertEqual(
            self.p1.location_address1,
            self.donation_information_payload["locationAddress1"],
        )
        self.assertEqual(
            self.p1.location_address2,
            self.donation_information_payload["locationAddress2"],
        )
        self.assertEqual(
            self.p1.location_city, self.donation_information_payload["locationCity"]
        )
        self.assertEqual(
            self.p1.location_country,
            self.donation_information_payload["locationCountry"],
        )

        # fake systempay webhook
        complete_payment(payment)
        donation_notification_listener(payment)
        on_commit.assert_called_once()

    def test_cannot_donate_without_required_fields(self):
        required_fields = [
            "nationality",
            "firstName",
            "lastName",
            "locationAddress1",
            "locationZip",
            "locationCity",
            "locationCountry",
        ]

        for f in required_fields:
            d = self.donation_information_payload.copy()
            del d[f]

            res = self.client.post(self.create_donation_url, d)
            self.assertEqual(
                res.status_code,
                422,
            )

    def test_create_person_when_using_new_address(self):
        self.donation_information_payload["email"] = "test2@test.com"
        res = self.client.post(
            self.create_donation_url, self.donation_information_payload
        )

        payment = Payment.objects.get()
        self.assertEqual(res.status_code, 200)
        self.assertIn(front_url("payment_page", args=(payment.pk,)), res.data["next"])

        # simulate correct payment
        complete_payment(payment)
        donation_notification_listener(payment)

        p2 = Person.objects.exclude(pk=self.p1.pk).get()
        # assert fields have been saved on model
        self.assertEqual(p2.first_name, self.donation_information_payload["firstName"])
        self.assertEqual(p2.last_name, self.donation_information_payload["lastName"])
        self.assertEqual(
            p2.location_address1,
            self.donation_information_payload["locationAddress1"],
        )
        self.assertEqual(
            p2.location_address2,
            self.donation_information_payload["locationAddress2"],
        )
        self.assertEqual(
            p2.location_city, self.donation_information_payload["locationCity"]
        )
        self.assertEqual(
            p2.location_country,
            self.donation_information_payload["locationCountry"],
        )

        # assert user fields have been saved on payment
        self.assertEqual(
            payment.first_name, self.donation_information_payload["firstName"]
        )
        self.assertEqual(
            payment.last_name, self.donation_information_payload["lastName"]
        )
        self.assertEqual(
            payment.phone_number, self.donation_information_payload["contactPhone"]
        )

    def test_cannot_donate_to_uncertified_group(self):
        self.group.subtypes.all().delete()
        self.client.force_login(self.p1.role)

        res = self.client.get(self.amount_url)
        self.assertEqual(res.status_code, 200)
        allocations = [
            {"type": "group", "group": str(self.group.pk), "amount": 10000},
            {"type": "group", "group": str(self.other_group.pk), "amount": 5000},
        ]
        res = self.client.post(
            self.create_donation_url,
            {
                **self.donation_information_payload,
                "paymentTiming": donations.serializers.SINGLE_TIME,
                "amount": "200",
                "allocations": allocations,
            },
        )
        self.assertEqual(res.status_code, 422)

    @using_separate_redis_server
    def test_can_donate_with_allocation(self):
        self.client.force_login(self.p1.role)

        res = self.client.get(self.amount_url)
        self.assertEqual(res.status_code, 200)

        res = self.client.get(self.information_modal_url)
        self.assertEqual(res.status_code, 200)
        allocations = [
            {"type": "group", "group": str(self.group.pk), "amount": 10000},
            {"type": "group", "group": str(self.other_group.pk), "amount": 5000},
        ]
        res = self.client.post(
            self.create_donation_url,
            {**self.donation_information_payload, "allocations": allocations},
        )
        # no other payment
        payment = Payment.objects.get()
        self.assertEqual(res.status_code, 200)
        self.assertIn(front_url("payment_page", args=(payment.pk,)), res.data["next"])

        self.assertIn("allocations", payment.meta)
        self.assertEqual(
            payment.meta["allocations"],
            json.dumps(allocations),
        )

        complete_payment(payment)
        donation_notification_listener(payment)

        self.assertTrue(
            Operation.objects.filter(group=self.group, amount=10000, payment=payment)
        )
        self.assertTrue(
            Operation.objects.filter(
                group=self.other_group, amount=5000, payment=payment
            )
        )

    def test_allocation_createdmeta_on_payment(self):
        payment = create_payment(
            person=self.p1,
            type=DonsConfig.SINGLE_TIME_DONATION_TYPE,
            price=10000,
            mode=SystemPayPaymentMode.id,
            meta={"allocations": json.dumps({str(self.group.pk): 10000})},
        )

        complete_payment(payment)
        notify_status_change(payment)

        self.assertTrue(Operation.objects.exists())
        operation = Operation.objects.get()

        self.assertEqual(operation.amount, 10000)
        self.assertEqual(operation.group, self.group)


class MonthlyDonationTestCase(DonationTestMixin, APITestCase):
    def create_subscription(self, person, amount, allocations=None):
        s = Subscription.objects.create(
            person=person,
            price=amount,
            status=Subscription.STATUS_ACTIVE,
            type=DonsConfig.MONTHLY_DONATION_TYPE,
            mode=payment_modes.DEFAULT_MODE,
        )

        # création d'un faux alias et d'une fausse SystemPaySubscription
        alias = SystemPayAlias.objects.create(
            identifier=uuid.uuid4(),
            active=True,
            expiry_date=timezone.now() + timezone.timedelta(days=365),
        )

        SystemPaySubscription.objects.create(
            identifier="fake_sub", subscription=s, alias=alias
        )

        if allocations:
            for group, amount in allocations.items():
                MonthlyAllocation.objects.create(
                    subscription=s, group=group, amount=amount
                )

        return s

    @mock.patch("django.db.transaction.on_commit")
    def test_can_make_monthly_donation_while_logged_in(self, on_commit):
        self.client.force_login(self.p1.role)

        res = self.client.get(self.amount_url)
        self.assertEqual(res.status_code, 200)

        res = self.client.get(self.information_modal_url)
        self.assertEqual(res.status_code, 200)

        res = self.client.post(
            self.create_donation_url,
            {
                **self.donation_information_payload,
                "paymentTiming": donations.serializers.MONTHLY,
                "allocations": [{"group": str(self.group.pk), "amount": 10000}],
            },
        )
        subscription = Subscription.objects.last()
        self.assertTrue(MonthlyAllocation.objects.exists())
        allocation = MonthlyAllocation.objects.last()
        self.assertEqual(allocation.subscription, subscription)
        self.assertEqual(allocation.amount, 10000)
        self.assertEqual(allocation.group, self.group)
        self.assertEqual(res.status_code, 200)
        self.assertIn(
            reverse("subscription_page", args=[subscription.pk]), res.data["next"]
        )

        self.p1.refresh_from_db()

        self.assertEqual(
            self.p1.first_name, self.donation_information_payload["firstName"]
        )
        self.assertEqual(
            self.p1.last_name, self.donation_information_payload["lastName"]
        )
        self.assertEqual(
            self.p1.location_address1,
            self.donation_information_payload["locationAddress1"],
        )
        self.assertEqual(
            self.p1.location_address2,
            self.donation_information_payload["locationAddress2"],
        )
        self.assertEqual(
            self.p1.location_city, self.donation_information_payload["locationCity"]
        )
        self.assertEqual(
            self.p1.location_country,
            self.donation_information_payload["locationCountry"],
        )

        complete_subscription(subscription)
        monthly_donation_subscription_listener(subscription)
        # fake systempay webhook
        on_commit.assert_called_once()
        self.assertIsInstance(on_commit.call_args[0][0], partial)
        self.assertEqual(on_commit.call_args[0][0].func, send_donation_email.delay)

        auto_payment = create_payment(
            person=self.p1,
            type=subscription.type,
            price=subscription.price,
            subscription=subscription,
            status=Payment.STATUS_COMPLETED,
        )

        donation_notification_listener(payment=auto_payment)

        operation = Operation.objects.get()
        self.assertEqual(operation.group, self.group)
        self.assertEqual(operation.amount, 10000)

        # vérifions que c'est idempotent
        donation_notification_listener(payment=auto_payment)
        operation = Operation.objects.get()
        self.assertEqual(operation.group, self.group)
        self.assertEqual(operation.amount, 10000)

    def test_can_also_create_monthly_donation_from_profile(self):
        self.client.force_login(self.p1.role)
        profile_payments_page = reverse("view_payments")
        res = self.client.get(profile_payments_page)
        self.assertEqual(res.status_code, 200)
        res = self.client.post(
            profile_payments_page,
            urlencode(
                {
                    "type": donations.serializers.MONTHLY,
                    "amount": "200",
                    "group": str(self.group.pk),
                    "allocation": "100",
                }
            ),
            content_type="application/x-www-form-urlencoded",
        )
        self.assertRedirects(res, self.information_modal_url)

    def test_can_see_monthly_payment_from_profile(self):
        s = self.create_subscription(
            person=self.p1, amount=1000, allocations={self.group: 600}
        )
        self.client.force_login(self.p1.role)

        profile_payments_page = reverse("view_payments")
        res = self.client.get(profile_payments_page)

        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "<h5>Don mensuel à l'AFLFI</h5>", html=True)
        self.assertContains(res, "Vous donnez <strong>10,00\u00A0€</strong>")
        self.assertContains(
            res,
            "<li><strong>6,00\u00A0€ aux actions du groupe &laquo;&nbsp;Groupe&nbsp;&raquo;</strong></li>",
            html=True,
        )
        self.assertContains(
            res,
            "<li><strong>4,00\u00A0€ aux actions et campagnes nationales</strong>, ainsi qu'aux outils mis à la disposition des insoumis⋅es (comme Action populaire&nbsp;!).</li>",
            html=True,
        )

    @mock.patch(
        "agir.donations.views.api_views.send_monthly_donation_confirmation_email"
    )
    def test_create_person_when_using_new_address(self, send_email):
        res = self.client.get(self.information_modal_url)
        self.assertEqual(res.status_code, 200)

        self.donation_information_payload["email"] = "test2@test.com"
        res = self.client.post(
            self.create_donation_url,
            {
                **self.donation_information_payload,
                "paymentTiming": donations.serializers.MONTHLY,
                "allocations": [],
            },
        )

        self.assertEqual(res.status_code, 200)
        self.assertIn(
            reverse("monthly_donation_confirmation_email_sent"), res.data["next"]
        )

        send_email.delay.assert_called_once()
        expected = {
            "email": "test2@test.com",
            "confirmation_view_name": "monthly_donation_confirm",
            "amount": 20000,
            "allocations": "[]",
            "payment_mode": payment_modes.DEFAULT_MODE,
            "nationality": "FR",
            "first_name": "Marc",
            "last_name": "Frank",
            "location_address1": "4 rue de Chaume",
            "location_address2": "",
            "location_zip": "33000",
            "location_city": "Bordeaux",
            "location_country": "FR",
            "contact_phone": "+33645789845",
        }
        for key, value in expected.items():
            self.assertIn(key, send_email.delay.call_args[1])
            self.assertEqual(send_email.delay.call_args[1][key], value)

        send_monthly_donation_confirmation_email(**expected)

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]

        confirm_subscription_url = reverse("monthly_donation_confirm")
        m = re.search(rf"{confirm_subscription_url}\?[^\s]+", email.body)
        url_with_params = m.group(0)

        res = self.client.get(url_with_params)
        subscription = Subscription.objects.get()
        self.assertRedirects(res, reverse("subscription_page", args=(subscription.pk,)))

        # simulate correct payment
        complete_subscription(subscription)
        monthly_donation_subscription_listener(subscription)

        p2 = Person.objects.exclude(pk=self.p1.pk).get()
        # assert fields have been saved on model
        self.assertEqual(p2.first_name, self.donation_information_payload["firstName"])
        self.assertEqual(p2.last_name, self.donation_information_payload["lastName"])
        self.assertEqual(
            p2.location_address1,
            self.donation_information_payload["locationAddress1"],
        )
        self.assertEqual(
            p2.location_address2,
            self.donation_information_payload["locationAddress2"],
        )
        self.assertEqual(
            p2.location_city, self.donation_information_payload["locationCity"]
        )
        self.assertEqual(
            p2.location_country,
            self.donation_information_payload["locationCountry"],
        )

    @mock.patch("agir.donations.views.donations_views.replace_subscription")
    def test_can_modify_subscription(self, replace_subscription):
        s = self.create_subscription(
            person=self.p1, amount=1000, allocations={self.group: 600}
        )

        self.client.force_login(self.p1.role)

        res = self.client.post(
            reverse("view_payments"),
            {
                "amount": "1200",
                "allocations": json.dumps(
                    [{"group": str(self.group.pk), "amount": 700}]
                ),
                "previous_subscription": s.id,
            },
        )

        res = self.client.post(
            self.create_donation_url,
            {
                **self.donation_information_payload,
                "amount": 700,
                "allocations": [{"group": str(self.group.pk), "amount": 700}],
                "paymentTiming": donations.serializers.MONTHLY,
            },
        )

        self.assertEqual(res.status_code, 200)
        self.assertIn(reverse("already_has_subscription"), res.data["next"])

        res = self.client.post(
            reverse("already_has_subscription"),
            urlencode({"choice": "A"}),
            content_type="application/x-www-form-urlencoded",
        )

        new_sub = Subscription.objects.exclude(pk=s.id).get()

        self.assertRedirects(res, reverse("view_payments"))
        replace_subscription.assert_called_once()
        self.assertEqual(
            tuple(replace_subscription.call_args),
            ((), {"previous_subscription": s, "new_subscription": new_sub}),
        )

    @mock.patch(
        "agir.donations.views.api_views.send_monthly_donation_confirmation_email"
    )
    def test_mail_sent_when_person_not_loggedin(self, send_email):
        existing_person = Person.objects.create_2022(
            "existing@person.test", create_role=True
        )
        res = self.client.get(self.information_modal_url)
        self.assertEqual(res.status_code, 200)
        allocations = [
            {"type": "group", "group": str(self.group.pk), "amount": 100},
            {"type": "group", "group": str(self.other_group.pk), "amount": 300},
        ]
        res = self.client.post(
            self.create_donation_url,
            data={
                "email": existing_person.email,
                **self.donation_information_payload,
                "paymentTiming": donations.serializers.MONTHLY,
                "amount": "500",
                "allocations": allocations,
            },
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn(
            reverse("monthly_donation_confirmation_email_sent"), res.data["next"]
        )
        send_email.delay.assert_called_once()
        expected = {
            "confirmation_view_name": "monthly_donation_confirm",
            "email": existing_person.email,
            "amount": 500,
            "allocations": json.dumps(allocations),
            "payment_mode": payment_modes.DEFAULT_MODE,
            "nationality": "FR",
            "first_name": "Marc",
            "last_name": "Frank",
            "location_address1": "4 rue de Chaume",
            "location_address2": "",
            "location_zip": "33000",
            "location_city": "Bordeaux",
            "location_country": "FR",
            "contact_phone": "+33645789845",
        }
        for key, value in expected.items():
            self.assertIn(key, send_email.delay.call_args[1])
            self.assertEqual(send_email.delay.call_args[1][key], value)

    def test_correct_email_content_when_not_logged_in(self):
        params = {
            "email": "text@test.com",
            "amount": 500,
            "allocations": json.dumps(
                {str(self.group.pk): 100, str(self.other_group.pk): 300}
            ),
            "payment_mode": payment_modes.DEFAULT_MODE,
            "nationality": "FR",
            "first_name": "Marc",
            "last_name": "Frank",
            "location_address1": "4 rue de Chaume",
            "location_address2": "",
            "location_zip": "33000",
            "location_city": "Bordeaux",
            "location_country": "FR",
            "contact_phone": "+33645789845",
        }

        send_monthly_donation_confirmation_email(
            **params, confirmation_view_name="monthly_donation_confirm"
        )

        self.assertEqual(len(mail.outbox), 1)

        params["token"] = monthly_donation_confirmation_token_generator.make_token(
            **params
        )
        expected_link = front_url("monthly_donation_confirm", query=params)
        email_text = mail.outbox[0].body

        self.assertIn(expected_link, email_text)

    def test_create_subscription_when_following_confirmation_link(self):
        s = self.create_subscription(
            person=self.p1, amount=1000, allocations={self.group: 600}
        )

        link_params = {
            "email": "test@test.com",
            "amount": 500,
            "allocations": json.dumps(
                {str(self.group.pk): 100, str(self.other_group.pk): 300}
            ),
            "nationality": "FR",
            "first_name": "Marc",
            "last_name": "Frank",
            "location_address1": "4 rue de Chaume",
            "location_address2": "",
            "location_zip": "33000",
            "location_city": "Bordeaux",
            "location_country": "FR",
            "contact_phone": "+33645789845",
        }

        link_params["token"] = monthly_donation_confirmation_token_generator.make_token(
            **link_params
        )

        res = self.client.get(reverse("monthly_donation_confirm"), data=link_params)
        self.assertRedirects(res, reverse("already_has_subscription"))
