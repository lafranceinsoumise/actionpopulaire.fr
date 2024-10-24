import string
import uuid
from datetime import timedelta
from random import choices
from unittest import mock
from urllib.parse import urlparse

from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from agir.donations.apps import DonsConfig
from agir.events.apps import EventsConfig
from agir.events.models import Event, RSVP, IdentifiedGuest
from agir.lib.tests.mixins import FakeDataMixin
from agir.payments.models import Payment, Subscription
from agir.people.models import Person
from agir.system_pay import SystemPayPaymentMode, SystemPayError
from agir.system_pay.crypto import get_signature
from agir.system_pay.models import SystemPayTransaction
from agir.system_pay.rest_api import (
    SystemPayRestAPI,
)
from agir.system_pay.utils import get_trans_id_from_order_id


def random_subscription_id():
    return "".join(choices(string.ascii_lowercase + string.digits, k=14))


def webhookcall_data(
    order_id,
    trans_id,
    operation_type,
    trans_status,
    amount,
    cust_id,
    trans_uuid=None,
    identifier=None,
    expiry_year=None,
    expiry_month=None,
    subscription=None,
    generate_subscription=False,
    generate_alias=False,
):
    expiry_date = timezone.now() + timezone.timedelta(days=200)
    systempay_data = {
        "vads_trans_status": trans_status,
        "vads_order_id": order_id,
        "vads_trans_id": trans_id,
        "vads_trans_uuid": trans_uuid or uuid.uuid4().hex,
        "vads_operation_type": operation_type,
        "vads_amount": str(amount),
        "vads_cust_id": str(cust_id),
        "vads_identifier": uuid.uuid4().hex if generate_alias else identifier,
        "vads_expiry_year": expiry_year
        or (expiry_date.year if identifier or generate_alias else None),
        "vads_expiry_month": expiry_month
        or (expiry_date.month if identifier or generate_alias else None),
        "vads_subscription": (
            random_subscription_id() if generate_subscription else subscription
        ),
    }

    systempay_data = {k: v for k, v in systempay_data.items() if v is not None}

    systempay_data["signature"] = get_signature(
        systempay_data, certificate=settings.SYSTEMPAY_CERTIFICATE
    )

    return systempay_data


class PaymentUXTestCase(FakeDataMixin, TestCase):
    def test_can_see_return_page_for_payment(self):
        payment = Payment.objects.create(
            person=self.data["people"]["user1"],
            email=self.data["people"]["user1"].email,
            price=1000,
            type=DonsConfig.SINGLE_TIME_DONATION_TYPE,
            mode=SystemPayPaymentMode.id,
        )
        self.client.force_login(self.data["people"]["user1"].role)

        res = self.client.get(reverse("payment_page", args=[payment.pk]))

        self.assertEqual(
            res.get("Cache-control"),
            "max-age=0, no-cache, no-store, must-revalidate, private",
        )

        initial = res.context_data["form"].initial

        transaction_id = initial["vads_order_id"]

        self.assertEqual(initial["vads_amount"], 1000)
        self.assertEqual(initial["vads_cust_email"], self.data["people"]["user1"].email)
        self.assertEqual(initial["vads_cust_email"], self.data["people"]["user1"].email)

        success_url = urlparse(initial["vads_url_success"])
        error_url = urlparse(initial["vads_url_error"])
        self.assertEqual(success_url.path, f"/paiement/{payment.id}/retour/")
        self.assertEqual(error_url.path, f"/paiement/carte/retour/{transaction_id}/")
        self.assertEqual(error_url.query, "status=error")

        res = self.client.get(f"/paiement/{payment.id}/retour/")
        self.assertEqual(res.status_code, status.HTTP_302_FOUND)

        res = self.client.get(f"/paiement/carte/retour/{transaction_id}/?status=error")
        self.assertContains(res, "<h1>Paiement échoué</h1>")


class WebhookTestCase(FakeDataMixin, TestCase):
    @mock.patch("agir.donations.views.donations_views.send_donation_email")
    def test_transaction_ok(self, send_donation_email):
        payment = Payment.objects.create(
            person=self.data["people"]["user1"],
            price=1000,
            type=DonsConfig.SINGLE_TIME_DONATION_TYPE,
            mode=SystemPayPaymentMode.id,
        )

        self.client.force_login(self.data["people"]["user1"].role)

        res = self.client.get(reverse("payment_page", args=[payment.pk]))
        self.assertContains(res, "vads")
        self.assertEqual(
            1, SystemPayTransaction.objects.filter(payment=payment).count()
        )

        res = self.client.get(reverse("payment_retry", args=[payment.pk]))
        self.assertContains(res, "vads")
        self.assertEqual(
            2, SystemPayTransaction.objects.filter(payment=payment).count()
        )

        self.client.logout()

        order_id = SystemPayTransaction.objects.filter(payment=payment).last().pk
        systempay_data = webhookcall_data(
            order_id=order_id,
            trans_id=get_trans_id_from_order_id(order_id),
            operation_type="DEBIT",
            trans_status="AUTHORISED",
            amount=payment.price,
            cust_id=payment.person.pk,
        )

        res = self.client.post(reverse("system_pay:webhook"), systempay_data)
        self.assertEqual(res.status_code, 200)
        payment.refresh_from_db()
        self.assertEqual(payment.status, Payment.STATUS_COMPLETED)
        self.assertEqual(
            2, SystemPayTransaction.objects.filter(payment=payment).count()
        )

        systempay_data = webhookcall_data(
            order_id=order_id,
            trans_id=get_trans_id_from_order_id(order_id),
            operation_type="DEBIT",
            trans_status="REFUSED",
            amount=payment.price,
            cust_id=payment.person.pk,
        )

        res = self.client.post(reverse("system_pay:webhook"), systempay_data)
        self.assertEqual(res.status_code, 200)
        payment.refresh_from_db()
        self.assertEqual(payment.status, Payment.STATUS_COMPLETED)
        self.assertEqual(
            2, SystemPayTransaction.objects.filter(payment=payment).count()
        )

    @mock.patch("agir.donations.views.donations_views.send_donation_email")
    def test_transaction_on_canceled_payment(self, send_donation_email):
        payment = Payment.objects.create(
            person=self.data["people"]["user1"],
            price=1000,
            type=DonsConfig.SINGLE_TIME_DONATION_TYPE,
            mode=SystemPayPaymentMode.id,
        )

        self.client.force_login(self.data["people"]["user1"].role)

        res = self.client.get(reverse("payment_page", args=[payment.pk]))
        self.assertContains(res, "vads")
        self.assertEqual(
            1, SystemPayTransaction.objects.filter(payment=payment).count()
        )

        payment.status = Payment.STATUS_CANCELED
        payment.save()

        self.client.logout()

        order_id = SystemPayTransaction.objects.filter(payment=payment).last().pk
        systempay_data = webhookcall_data(
            order_id=order_id,
            trans_id=get_trans_id_from_order_id(order_id),
            operation_type="DEBIT",
            trans_status="AUTHORISED",
            amount=payment.price,
            cust_id=payment.person.pk,
        )

        res = self.client.post(reverse("system_pay:webhook"), systempay_data)
        self.assertEqual(res.status_code, 200)
        payment.refresh_from_db()
        self.assertEqual(payment.status, Payment.STATUS_CANCELED)

    @mock.patch.object(SystemPayRestAPI, "cancel_alias")
    @mock.patch("agir.donations.views.donations_views.send_donation_email")
    def test_subscription(self, send_donation_email, cancel_alias):
        subscription = Subscription.objects.create(
            person=self.data["people"]["user1"],
            price=1000,
            type=DonsConfig.SINGLE_TIME_DONATION_TYPE,
            mode=SystemPayPaymentMode.id,
        )

        self.client.force_login(self.data["people"]["user1"].role)

        res = self.client.get(reverse("subscription_page", args=[subscription.pk]))
        self.assertContains(res, "vads")
        self.assertEqual(
            1, SystemPayTransaction.objects.filter(subscription=subscription).count()
        )

        self.client.logout()

        order_id = (
            SystemPayTransaction.objects.filter(subscription=subscription).last().pk
        )

        systempay_data = webhookcall_data(
            order_id=order_id,
            trans_id=get_trans_id_from_order_id(order_id),
            operation_type="VERIFICATION",
            trans_status="ACCEPTED",
            amount=0,
            cust_id=subscription.person.pk,
            generate_alias=True,
            generate_subscription=True,
        )

        res = self.client.post(reverse("system_pay:webhook"), systempay_data)

        self.assertEqual(res.status_code, 200)
        subscription.refresh_from_db()
        self.assertEqual(subscription.status, Subscription.STATUS_ACTIVE)
        self.assertEqual(subscription.payments.all().count(), 0)

        sp_sub = subscription.system_pay_subscriptions.get(active=True)
        alias = sp_sub.alias

        systempay_data = webhookcall_data(
            order_id=order_id,
            trans_id=get_trans_id_from_order_id(
                order_id + 10
            ),  # new transaction, created by systempay
            operation_type="DEBIT",
            trans_status="CAPTURED",
            amount=1000,
            cust_id=subscription.person.pk,
            identifier=alias.identifier.hex,
            subscription=sp_sub.identifier,
        )

        res = self.client.post(reverse("system_pay:webhook"), systempay_data)

        self.assertEqual(res.status_code, 200)
        subscription.refresh_from_db()
        self.assertEqual(subscription.payments.all().count(), 1)
        self.assertEqual(Payment.objects.first().status, Payment.STATUS_COMPLETED)
        self.assertEqual(Payment.objects.first().subscription, subscription)
        self.assertEqual(Payment.objects.first().price, 1000)

        # test indempotence
        res = self.client.post(reverse("system_pay:webhook"), systempay_data)
        self.assertEqual(res.status_code, 200)
        subscription.refresh_from_db()
        self.assertEqual(subscription.payments.all().count(), 1)
        self.assertEqual(Payment.objects.first().status, Payment.STATUS_COMPLETED)
        self.assertEqual(Payment.objects.first().subscription, subscription)
        self.assertEqual(Payment.objects.first().price, 1000)

        # test refused payment
        trans_uuid = uuid.uuid4().hex
        systempay_data["vads_trans_uuid"] = trans_uuid
        systempay_data["vads_trans_status"] = "REFUSED"
        systempay_data["signature"] = get_signature(
            systempay_data, settings.SYSTEMPAY_CERTIFICATE
        )
        res = self.client.post(reverse("system_pay:webhook"), systempay_data)
        self.assertEqual(res.status_code, 200)
        subscription.refresh_from_db()
        self.assertEqual(subscription.payments.all().count(), 2)
        self.assertEqual(Payment.objects.first().status, Payment.STATUS_REFUSED)
        self.assertEqual(Payment.objects.first().subscription, subscription)
        self.assertEqual(Payment.objects.first().price, 1000)

        # test payment card change
        res = self.client.get(reverse("subscription_page", args=[subscription.pk]))
        self.assertContains(res, "vads")
        self.assertEqual(
            2, SystemPayTransaction.objects.filter(subscription=subscription).count()
        )

        order_id = (
            SystemPayTransaction.objects.filter(subscription=subscription).last().pk
        )

        systempay_data = webhookcall_data(
            order_id=order_id,
            trans_id=get_trans_id_from_order_id(order_id),
            operation_type="VERIFICATION",
            trans_status="ACCEPTED",
            amount=0,
            cust_id=subscription.person.pk,
            generate_alias=True,
            generate_subscription=True,
        )

        res = self.client.post(reverse("system_pay:webhook"), systempay_data)

        self.assertEqual(res.status_code, 200)
        subscription.refresh_from_db()
        self.assertEqual(subscription.status, Subscription.STATUS_ACTIVE)

        self.assertEqual(2, subscription.system_pay_subscriptions.count())
        self.assertEqual(
            1, subscription.system_pay_subscriptions.filter(active=True).count()
        )

        cancel_alias.assert_called_with(
            subscription.system_pay_subscriptions.get(active=False).alias
        )


class CancelOrRefundPaymentTestCase(TestCase):
    def create_payment(self, **kwargs):
        payment = Payment.objects.create(
            mode=SystemPayPaymentMode.id,
            status=Payment.STATUS_COMPLETED,
            person=kwargs.pop("person", self.person),
            price=kwargs.pop("price", 1000),
            type=kwargs.pop("type", DonsConfig.SINGLE_TIME_DONATION_TYPE),
            meta=kwargs.pop("meta", {"VERSION": 2}),
            **kwargs,
        )
        payment.systempaytransaction_set.add(
            SystemPayTransaction.objects.create(
                status=SystemPayTransaction.STATUS_COMPLETED, uuid=uuid.uuid4()
            )
        )
        return payment

    def setUp(self):
        self.person = Person.objects.create_insoumise("person@agir.local")
        event = Event.objects.create(
            name="Event",
            start_time=timezone.now() + timedelta(days=3),
            end_time=timezone.now() + timedelta(days=4),
            allow_guests=True,
        )
        self.rsvp_payment = self.create_payment(
            type=EventsConfig.PAYMENT_TYPE,
            meta={"VERSION": "2", "is_guest": False},
        )
        self.rsvp = RSVP.objects.create(
            status=RSVP.Status.CONFIRMED,
            event=event,
            person=self.person,
            payment=self.rsvp_payment,
        )
        self.guest_payment = self.create_payment(
            type=EventsConfig.PAYMENT_TYPE, meta={"VERSION": "2", "is_guest": True}
        )
        self.guest = IdentifiedGuest.objects.create(
            rsvp=self.rsvp,
            status=RSVP.Status.CONFIRMED,
            payment=self.guest_payment,
        )
        self.payment_mode = SystemPayPaymentMode()
        self.mock_api_response = {
            "status": "PAID",
            "detailedStatus": "AUTHORISED",
            "operationType": "CREDIT",
        }

    @mock.patch.object(SystemPayRestAPI, "cancel_or_refund_transaction")
    def test_payment_transaction_can_be_cancelled(self, rest_api):
        rest_api.return_value = False, self.mock_api_response
        payment = self.create_payment()
        transaction = (
            payment.systempaytransaction_set.filter(
                status=SystemPayTransaction.STATUS_COMPLETED, uuid__isnull=False
            )
            .order_by("-created")
            .first()
        )
        self.assertEqual(payment.status, Payment.STATUS_COMPLETED)
        self.assertEqual(transaction.status, SystemPayTransaction.STATUS_COMPLETED)
        self.payment_mode.cancel_or_refund_payment_action(payment)
        payment.refresh_from_db()
        transaction.refresh_from_db()
        self.assertEqual(payment.status, Payment.STATUS_REFUND)
        self.assertEqual(transaction.status, SystemPayTransaction.STATUS_CANCELED)

    @mock.patch.object(SystemPayRestAPI, "cancel_or_refund_transaction")
    def test_payment_transaction_can_be_refunded(self, rest_api):
        rest_api.return_value = True, self.mock_api_response
        payment = self.create_payment()
        transaction = (
            payment.systempaytransaction_set.filter(
                status=SystemPayTransaction.STATUS_COMPLETED, uuid__isnull=False
            )
            .order_by("-created")
            .first()
        )
        self.assertEqual(payment.status, Payment.STATUS_COMPLETED)
        self.assertEqual(transaction.status, SystemPayTransaction.STATUS_COMPLETED)
        self.payment_mode.cancel_or_refund_payment_action(payment)
        payment.refresh_from_db()
        transaction.refresh_from_db()
        self.assertEqual(payment.status, Payment.STATUS_REFUND)
        self.assertEqual(transaction.status, SystemPayTransaction.STATUS_REFUNDED)

    @mock.patch.object(SystemPayRestAPI, "cancel_or_refund_transaction")
    def test_payment_is_not_refunded_if_no_completed_transanction_is_found(
        self, rest_api
    ):
        rest_api.side_effect = SystemPayError("Oh nooooo !", system_pay_code="PSP_OHNO")
        payment = self.create_payment()
        transaction = (
            payment.systempaytransaction_set.filter(
                status=SystemPayTransaction.STATUS_COMPLETED, uuid__isnull=False
            )
            .order_by("-created")
            .first()
        )
        self.assertEqual(payment.status, Payment.STATUS_COMPLETED)
        transaction.status = SystemPayTransaction.STATUS_WAITING
        transaction.save()
        transaction.refresh_from_db()
        self.assertEqual(transaction.status, SystemPayTransaction.STATUS_WAITING)
        with self.assertRaises(ValueError):
            self.payment_mode.cancel_or_refund_payment_action(payment)
            payment.refresh_from_db()
            transaction.refresh_from_db()
            self.assertEqual(payment.status, Payment.STATUS_COMPLETED)
            self.assertEqual(transaction.status, SystemPayTransaction.STATUS_COMPLETED)

    @mock.patch.object(SystemPayRestAPI, "cancel_or_refund_transaction")
    def test_payment_is_not_refunded_if_transanction_has_no_id(self, rest_api):
        rest_api.side_effect = SystemPayError("Oh nooooo !", system_pay_code="PSP_OHNO")
        payment = self.create_payment()
        transaction = (
            payment.systempaytransaction_set.filter(
                status=SystemPayTransaction.STATUS_COMPLETED, uuid__isnull=False
            )
            .order_by("-created")
            .first()
        )
        self.assertEqual(payment.status, Payment.STATUS_COMPLETED)
        self.assertEqual(transaction.status, SystemPayTransaction.STATUS_COMPLETED)
        transaction.uuid = None
        transaction.save()
        with self.assertRaises(ValueError):
            self.payment_mode.cancel_or_refund_payment_action(payment)
            payment.refresh_from_db()
            transaction.refresh_from_db()
            self.assertEqual(payment.status, Payment.STATUS_COMPLETED)
            self.assertEqual(transaction.status, SystemPayTransaction.STATUS_COMPLETED)

    @mock.patch.object(SystemPayRestAPI, "cancel_or_refund_transaction")
    @mock.patch("agir.system_pay.logger")
    def test_payment_is_not_refunded_if_rest_api_raise_an_error(self, logger, rest_api):
        rest_api.side_effect = SystemPayError("Oh nooooo !", system_pay_code="PSP_OHNO")
        payment = self.create_payment()
        transaction = (
            payment.systempaytransaction_set.filter(
                status=SystemPayTransaction.STATUS_COMPLETED, uuid__isnull=False
            )
            .order_by("-created")
            .first()
        )
        self.assertEqual(payment.status, Payment.STATUS_COMPLETED)
        self.assertEqual(transaction.status, SystemPayTransaction.STATUS_COMPLETED)
        logger.error.assert_not_called()
        with self.assertRaises(SystemPayError):
            self.payment_mode.cancel_or_refund_payment_action(payment)
            logger.error.called()
            payment.refresh_from_db()
            transaction.refresh_from_db()
            self.assertEqual(payment.status, Payment.STATUS_COMPLETED)
            self.assertEqual(transaction.status, SystemPayTransaction.STATUS_COMPLETED)

    @mock.patch.object(SystemPayRestAPI, "cancel_or_refund_transaction")
    def test_refunding_a_payment_cancels_the_related_rsvp(self, rest_api):
        rest_api.return_value = True, self.mock_api_response
        payment = self.rsvp_payment
        transaction = (
            payment.systempaytransaction_set.filter(
                status=SystemPayTransaction.STATUS_COMPLETED, uuid__isnull=False
            )
            .order_by("-created")
            .first()
        )
        self.assertEqual(payment.status, Payment.STATUS_COMPLETED)
        self.assertEqual(transaction.status, SystemPayTransaction.STATUS_COMPLETED)
        self.assertEqual(self.rsvp.status, RSVP.Status.CONFIRMED)
        self.payment_mode.cancel_or_refund_payment_action(payment)
        payment.refresh_from_db()
        transaction.refresh_from_db()
        self.rsvp.refresh_from_db()
        self.guest.refresh_from_db()
        self.assertEqual(payment.status, Payment.STATUS_REFUND)
        self.assertEqual(transaction.status, SystemPayTransaction.STATUS_REFUNDED)
        self.assertEqual(self.rsvp.status, RSVP.Status.CANCELLED)
        self.assertEqual(self.guest_payment.status, Payment.STATUS_COMPLETED)
        self.assertEqual(self.guest.status, RSVP.Status.CONFIRMED)

    @mock.patch.object(SystemPayRestAPI, "cancel_or_refund_transaction")
    def test_refunding_a_payment_cancels_the_related_identified_guest(self, rest_api):
        rest_api.return_value = True, self.mock_api_response
        payment = self.guest_payment
        transaction = (
            payment.systempaytransaction_set.filter(
                status=SystemPayTransaction.STATUS_COMPLETED, uuid__isnull=False
            )
            .order_by("-created")
            .first()
        )
        self.assertEqual(payment.status, Payment.STATUS_COMPLETED)
        self.assertEqual(transaction.status, SystemPayTransaction.STATUS_COMPLETED)
        self.assertEqual(self.guest.status, RSVP.Status.CONFIRMED)
        self.payment_mode.cancel_or_refund_payment_action(payment)
        payment.refresh_from_db()
        transaction.refresh_from_db()
        self.rsvp.refresh_from_db()
        self.guest.refresh_from_db()
        self.assertEqual(payment.status, Payment.STATUS_REFUND)
        self.assertEqual(transaction.status, SystemPayTransaction.STATUS_REFUNDED)
        self.assertEqual(self.guest.status, RSVP.Status.CANCELLED)
        self.assertEqual(self.rsvp_payment.status, Payment.STATUS_COMPLETED)
        self.assertEqual(self.rsvp.status, RSVP.Status.CONFIRMED)
