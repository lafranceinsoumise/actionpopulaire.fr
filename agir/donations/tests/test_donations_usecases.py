import json
from functools import partial
from unittest import mock

import re
import uuid
from django.conf import settings
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from agir.api.redis import using_separate_redis_server
from agir.donations.apps import DonsConfig
from agir.donations.forms import AllocationDonationForm
from agir.donations.models import Operation, MonthlyAllocation
from agir.donations.tasks import (
    send_monthly_donation_confirmation_email,
    send_donation_email,
)
from agir.groups.models import SupportGroup, Membership, SupportGroupSubtype
from agir.lib.utils import front_url
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
from ...authentication.tokens import monthly_donation_confirmation_token_generator
from ...system_pay.models import SystemPayAlias, SystemPaySubscription


class DonationTestMixin:
    def setUp(self):
        self.p1 = Person.objects.create_insoumise("test@test.com", create_role=True)

        self.donation_information_payload = {
            "amount": "20000",
            "allocations": "{}",
            "declaration": "Y",
            "nationality": "FR",
            "first_name": "Marc",
            "last_name": "Frank",
            "location_address1": "4 rue de Chaume",
            "location_address2": "",
            "location_zip": "33000",
            "location_city": "Bordeaux",
            "location_country": "FR",
            "contact_phone": "+33645789845",
            "mode": "check_donations",
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


class DonationTestCase(DonationTestMixin, TestCase):
    @mock.patch("django.db.transaction.on_commit")
    def test_can_donate_while_logged_in(self, on_commit):
        self.client.force_login(self.p1.role)
        amount_url = reverse("donation_amount")
        information_url = reverse("donation_information")

        res = self.client.get(amount_url)
        self.assertEqual(res.status_code, 200)

        res = self.client.post(
            amount_url,
            {"type": AllocationDonationForm.TYPE_SINGLE_TIME, "amount": "200"},
        )
        self.assertRedirects(res, information_url)

        res = self.client.get(information_url)
        self.assertEqual(res.status_code, 200)

        res = self.client.post(information_url, self.donation_information_payload)
        # no other payment
        payment = Payment.objects.get()
        self.assertRedirects(res, front_url("payment_page", args=(payment.pk,)))

        res = self.client.get(reverse("payment_return", args=(payment.pk,)))
        self.assertEqual(res.status_code, 200)

        self.p1.refresh_from_db()

        # assert fields have been saved on model
        for f in [
            "first_name",
            "last_name",
            "location_address1",
            "location_address2",
            "location_zip",
            "location_city",
            "location_country",
        ]:
            self.assertEqual(getattr(self.p1, f), self.donation_information_payload[f])

        # check person is not unsubscribed
        self.assertIn(Person.NEWSLETTER_LFI, self.p1.newsletters)

        # fake systempay webhook
        complete_payment(payment)
        donation_notification_listener(payment)
        on_commit.assert_called_once()

    def test_cannot_donate_without_required_fields(self):
        information_url = reverse("donation_information")

        res = self.client.post(
            reverse("donation_amount"),
            {"type": AllocationDonationForm.TYPE_SINGLE_TIME, "amount": "200"},
        )
        self.assertRedirects(res, information_url)

        required_fields = [
            "declaration",
            "nationality",
            "first_name",
            "last_name",
            "location_address1",
            "location_zip",
            "location_city",
            "location_country",
        ]

        for f in required_fields:
            d = self.donation_information_payload.copy()
            del d[f]

            res = self.client.post(information_url, d)
            self.assertEqual(
                res.status_code,
                200,
                msg="Should not redirect when field '%s' missing" % f,
            )
            self.assertFormError(res, "form", f, "Ce champ est obligatoire.")

    def test_cannot_donate_without_asserting_fiscal_residency_when_foreigner(self):
        self.client.force_login(self.p1.role)

        information_url = reverse("donation_information")

        res = self.client.post(
            reverse("donation_amount"),
            {"type": AllocationDonationForm.TYPE_SINGLE_TIME, "amount": "200"},
        )
        self.assertRedirects(res, information_url)

        self.donation_information_payload["nationality"] = "ES"

        res = self.client.post(information_url, self.donation_information_payload)
        self.assertEqual(res.status_code, 200)

        self.donation_information_payload["fiscal_resident"] = "Y"
        self.donation_information_payload["location_country"] = "ES"
        res = self.client.post(information_url, self.donation_information_payload)
        self.assertEqual(res.status_code, 200)

        self.donation_information_payload["location_country"] = "FR"
        res = self.client.post(information_url, self.donation_information_payload)
        payment = Payment.objects.get()
        self.assertRedirects(res, front_url("payment_page", args=[payment.pk]))

    def test_create_person_when_using_new_address(self):
        information_url = reverse("donation_information")

        res = self.client.post(
            reverse("donation_amount"),
            {"type": AllocationDonationForm.TYPE_SINGLE_TIME, "amount": "200"},
        )
        self.assertRedirects(res, information_url)

        self.donation_information_payload["email"] = "test2@test.com"
        res = self.client.post(information_url, self.donation_information_payload)
        payment = Payment.objects.get()
        self.assertRedirects(res, front_url("payment_page", args=[payment.pk]))

        # simulate correct payment
        complete_payment(payment)
        donation_notification_listener(payment)

        p2 = Person.objects.exclude(pk=self.p1.pk).get()
        # assert fields have been saved on model
        for f in [
            "first_name",
            "last_name",
            "location_address1",
            "location_address2",
            "location_zip",
            "location_city",
            "location_country",
            "email",
        ]:
            self.assertEqual(getattr(p2, f), self.donation_information_payload[f])

        self.assertNotIn(Person.NEWSLETTER_LFI, p2.newsletters)

    def test_create_and_subscribe_with_new_address(self):
        information_url = reverse("donation_information")

        res = self.client.post(
            reverse("donation_amount"),
            {"type": AllocationDonationForm.TYPE_SINGLE_TIME, "amount": "200"},
        )
        self.assertRedirects(res, information_url)

        self.donation_information_payload["email"] = "test2@test.com"
        res = self.client.post(
            information_url,
            {**self.donation_information_payload, "subscribed_lfi": "Y"},
        )
        payment = Payment.objects.get()
        self.assertRedirects(res, front_url("payment_page", args=[payment.pk]))

        self.assertTrue(payment.meta.get("subscribed_lfi"))

        # simulate correct payment
        complete_payment(payment)
        donation_notification_listener(payment)

        p2 = Person.objects.exclude(pk=self.p1.pk).get()
        self.assertIn(Person.NEWSLETTER_LFI, p2.newsletters)

    def test_cannot_donate_to_uncertified_group(self):
        self.group.subtypes.all().delete()
        self.client.force_login(self.p1.role)
        session = self.client.session

        amount_url = reverse("donation_amount")

        res = self.client.get(amount_url)
        self.assertEqual(res.status_code, 200)

        res = self.client.post(
            amount_url,
            {
                "type": AllocationDonationForm.TYPE_SINGLE_TIME,
                "amount": "200",
                "allocations": f'{{"group": "{str(self.group.pk)}", "amount": 10000}}',
            },
        )
        self.assertEqual(res.status_code, 200)
        self.assertNotIn("_donation_", session)

    @using_separate_redis_server
    def test_can_donate_with_allocation(self):
        self.client.force_login(self.p1.role)
        session = self.client.session

        amount_url = reverse("donation_amount")
        information_url = reverse("donation_information")

        res = self.client.get(amount_url)
        self.assertEqual(res.status_code, 200)

        res = self.client.post(
            amount_url,
            {
                "type": AllocationDonationForm.TYPE_SINGLE_TIME,
                "amount": "20000",
                "allocations": json.dumps(
                    [
                        {"group": str(self.group.pk), "amount": 10000},
                        {"group": str(self.other_group.pk), "amount": 5000},
                    ]
                ),
            },
        )
        self.assertRedirects(res, information_url)

        self.assertEqual(
            session["_donation_"]["allocations"],
            json.dumps(
                [
                    {"group": str(self.group.pk), "amount": 10000},
                    {"group": str(self.other_group.pk), "amount": 5000},
                ]
            ),
        )

        res = self.client.get(information_url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, self.group.pk)

        res = self.client.post(
            information_url,
            {
                **self.donation_information_payload,
                "allocations": json.dumps(
                    [
                        {"group": str(self.group.pk), "amount": 10000},
                        {"group": str(self.other_group.pk), "amount": 5000},
                    ]
                ),
            },
        )
        # no other payment
        payment = Payment.objects.get()
        self.assertRedirects(res, front_url("payment_page", args=(payment.pk,)))

        self.assertIn("allocations", payment.meta)
        self.assertEqual(
            payment.meta["allocations"],
            json.dumps({str(self.group.pk): 10000, str(self.other_group.pk): 5000}),
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
            type=DonsConfig.PAYMENT_TYPE,
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


class MonthlyDonationTestCase(DonationTestMixin, TestCase):
    def create_subscription(self, person, amount, allocations=None):
        s = Subscription.objects.create(
            person=person,
            price=amount,
            status=Subscription.STATUS_ACTIVE,
            type="don_mensuel",
            mode="system_pay",
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
        amount_url = reverse("donation_amount")
        information_url = reverse("monthly_donation_information")

        res = self.client.get(amount_url)
        self.assertEqual(res.status_code, 200)

        res = self.client.post(
            amount_url,
            {
                "type": AllocationDonationForm.TYPE_MONTHLY,
                "amount": "20000",
                "allocations": json.dumps(
                    [{"group": str(self.group.pk), "amount": 10000}]
                ),
            },
        )
        self.assertRedirects(res, information_url)

        res = self.client.get(information_url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "200,00")
        self.assertContains(res, "100,00")
        self.assertNotContains(res, " chèque")

        res = self.client.post(
            information_url,
            {
                **self.donation_information_payload,
                "allocations": json.dumps(
                    [{"group": str(self.group.pk), "amount": 10000}]
                ),
            },
        )
        # no other payment
        subscription = Subscription.objects.last()
        allocation = MonthlyAllocation.objects.last()
        self.assertEqual(allocation.subscription, subscription)
        self.assertEqual(allocation.amount, 10000)
        self.assertEqual(allocation.group, self.group)
        self.assertRedirects(res, reverse("subscription_page", args=(subscription.pk,)))

        self.p1.refresh_from_db()

        # assert fields have been saved on model
        for f in [
            "first_name",
            "last_name",
            "location_address1",
            "location_address2",
            "location_zip",
            "location_city",
            "location_country",
        ]:
            self.assertEqual(getattr(self.p1, f), self.donation_information_payload[f])

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
        information_url = reverse("monthly_donation_information")

        res = self.client.get(profile_payments_page)
        self.assertEqual(res.status_code, 200)

        res = self.client.post(
            profile_payments_page,
            {
                "type": AllocationDonationForm.TYPE_MONTHLY,
                "amount": "200",
                "group": str(self.group.pk),
                "allocation": "100",
            },
        )
        self.assertRedirects(res, information_url)

    def test_can_see_monthly_payment_from_profile(self):
        s = self.create_subscription(
            person=self.p1, amount=1000, allocations={self.group: 600}
        )
        self.client.force_login(self.p1.role)

        profile_payments_page = reverse("view_payments")
        res = self.client.get(profile_payments_page)

        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "<h4>Don mensuel à l'AFLFI</h4>", html=True)
        self.assertContains(res, "Vous donnez <strong>10,00\u00A0€</strong>")
        self.assertContains(
            res,
            "<li>4,00\u00A0€ sont alloués aux actions, aux campagnes nationales, et aux outils mis à la disposition des insoumis⋅es (comme cette plateforme internet).</li>",
            html=True,
        )
        self.assertContains(
            res,
            "<li>6,00\u00A0€ sont alloués aux actions du groupe &laquo;&nbsp;Groupe&nbsp;&raquo;</li>",
            html=True,
        )
        self.assertContains(
            res,
            f'<input type="hidden" name="previous_subscription" value="{s.id}" id="id_previous_subscription">',
            html=True,
        )

    @mock.patch(
        "agir.donations.views.donations_views.send_monthly_donation_confirmation_email"
    )
    def test_create_person_when_using_new_address(
        self, mock_send_monthly_donation_confirmation_email
    ):
        information_url = reverse("monthly_donation_information")

        res = self.client.post(
            reverse("donation_amount"),
            {"type": AllocationDonationForm.TYPE_MONTHLY, "amount": "200"},
        )
        self.assertRedirects(res, information_url)

        self.donation_information_payload["email"] = "test2@test.com"
        res = self.client.post(information_url, self.donation_information_payload)
        self.assertRedirects(res, reverse("monthly_donation_confirmation_email_sent"))
        mock_send_monthly_donation_confirmation_email.delay.assert_called_once()

        (
            task_args,
            task_kwargs,
        ) = mock_send_monthly_donation_confirmation_email.delay.call_args

        send_monthly_donation_confirmation_email(*task_args, **task_kwargs)

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
        for f in [
            "first_name",
            "last_name",
            "location_address1",
            "location_address2",
            "location_zip",
            "location_city",
            "location_country",
            "email",
        ]:
            self.assertEqual(getattr(p2, f), self.donation_information_payload[f])

    @mock.patch("agir.donations.views.donations_views.replace_subscription")
    def test_can_modify_subscription(self, replace_subscription):
        s = self.create_subscription(
            person=self.p1, amount=1000, allocations={self.group: 600}
        )

        self.client.force_login(self.p1.role)
        information_url = reverse("monthly_donation_information")
        session = self.client.session

        res = self.client.post(
            reverse("view_payments"),
            data={
                "amount": "1200",
                "allocations": json.dumps(
                    [{"group": str(self.group.pk), "amount": 700}]
                ),
                "previous_subscription": s.id,
            },
        )

        self.assertRedirects(res, information_url)
        self.assertEqual(session["_donation_"]["previous_subscription"], str(s.id))

        res = self.client.post(
            information_url,
            data={
                **self.donation_information_payload,
                "amount": 700,
                "allocations": json.dumps(
                    [{"group": str(self.group.pk), "amount": 700}]
                ),
                "previous_subscription": s.id,
            },
        )

        new_sub = Subscription.objects.exclude(pk=s.id).get()

        self.assertRedirects(res, reverse("view_payments"))
        replace_subscription.assert_called_once()
        self.assertEqual(
            tuple(replace_subscription.call_args),
            ((), {"previous_subscription": s, "new_subscription": new_sub}),
        )

    @mock.patch("agir.donations.views.donations_views.replace_subscription")
    def test_can_add_to_subscription(self, replace_subscription):
        s = self.create_subscription(
            person=self.p1, amount=1000, allocations={self.group: 600}
        )

        self.client.force_login(self.p1.role)
        information_url = reverse("monthly_donation_information")
        session = self.client.session

        res = self.client.post(
            reverse("donation_amount"),
            data={
                "type": "M",
                "amount": "500",
                "allocations": json.dumps(
                    [
                        {"group": str(self.group.pk), "amount": 100},
                        {"group": str(self.other_group.pk), "amount": 300},
                    ]
                ),
            },
        )

        self.assertRedirects(res, information_url)

        res = self.client.post(
            information_url,
            data={
                **self.donation_information_payload,
                "type": "M",
                "amount": "500",
                "allocations": json.dumps(
                    [
                        {"group": str(self.group.pk), "amount": 100},
                        {"group": str(self.other_group.pk), "amount": 300},
                    ]
                ),
            },
        )

        self.assertRedirects(res, reverse("already_has_subscription"))

        res = self.client.post(
            reverse("already_has_subscription"), data={"choice": "A"}
        )

        new_sub = Subscription.objects.exclude(pk=s.id).get()

        self.assertEqual(new_sub.price, 1500)
        self.assertDictEqual(
            {a.group: a.amount for a in new_sub.allocations.all()},
            {self.group: 700, self.other_group: 300},
        )

        self.assertRedirects(res, reverse("view_payments"))
        replace_subscription.assert_called_once()
        self.assertEqual(
            tuple(replace_subscription.call_args),
            ((), {"previous_subscription": s, "new_subscription": new_sub}),
        )

    @mock.patch(
        "agir.donations.views.donations_views.send_monthly_donation_confirmation_email"
    )
    def test_mail_sent_when_person_not_loggedin(self, send_email):
        information_url = reverse("monthly_donation_information")

        res = self.client.post(
            reverse("donation_amount"),
            data={
                "type": "M",
                "amount": "500",
                "allocations": json.dumps(
                    [
                        {"group": str(self.group.pk), "amount": 100},
                        {"group": str(self.other_group.pk), "amount": 300},
                    ]
                ),
            },
        )

        self.assertRedirects(res, information_url)

        res = self.client.post(
            information_url,
            data={
                "email": "test@test.com",  # existing user email
                "subscribed_lfi": "Y",
                **self.donation_information_payload,
                "type": "M",
                "amount": "500",
                "allocations": json.dumps(
                    [
                        {"group": str(self.group.pk), "amount": 100},
                        {"group": str(self.other_group.pk), "amount": 300},
                    ]
                ),
            },
        )

        self.assertRedirects(res, reverse("monthly_donation_confirmation_email_sent"))

        send_email.delay.assert_called_once()

        self.assertDictEqual(
            send_email.delay.call_args[1],
            {
                "email": "test@test.com",
                "subscription_total": 500,
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
                "subscribed_lfi": True,
            },
        )

    def test_correct_email_content_when_not_logged_in(self):
        params = {
            "email": "text@test.com",
            "subscription_total": 500,
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

        send_monthly_donation_confirmation_email(**params)

        self.assertEqual(len(mail.outbox), 1)

        params["token"] = monthly_donation_confirmation_token_generator.make_token(
            **params
        )
        expected_link = front_url("monthly_donation_confirm", query=params)
        email_text = mail.outbox[0].body

        self.assertIn(expected_link, email_text)

    @mock.patch("agir.donations.views.donations_views.replace_subscription")
    def test_create_subscription_when_following_confirmation_link(
        self, replace_subscription
    ):
        s = self.create_subscription(
            person=self.p1, amount=1000, allocations={self.group: 600}
        )

        link_params = {
            "email": "test@test.com",
            "subscription_total": 500,
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

        res = self.client.post(
            reverse("already_has_subscription"), data={"choice": "A"}
        )

        new_sub = Subscription.objects.exclude(pk=s.id).get()

        self.assertEqual(new_sub.price, 1500)
        self.assertDictEqual(
            {a.group: a.amount for a in new_sub.allocations.all()},
            {self.group: 700, self.other_group: 300},
        )

        self.assertRedirects(res, reverse("view_payments"))
        replace_subscription.assert_called_once()
        self.assertEqual(
            tuple(replace_subscription.call_args),
            ((), {"previous_subscription": s, "new_subscription": new_sub}),
        )
