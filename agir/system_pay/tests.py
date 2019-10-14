import uuid

from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from unittest import mock

from agir.donations.apps import DonsConfig
from agir.lib.tests.mixins import FakeDataMixin
from agir.payments.models import Payment, Subscription
from agir.system_pay import SystemPayPaymentMode
from agir.system_pay.crypto import get_signature
from agir.system_pay.models import SystemPayTransaction
from agir.system_pay.utils import vads_trans_id


class WebhookTestCase(FakeDataMixin, TestCase):
    @mock.patch("agir.donations.views.send_donation_email")
    def test_transaction_ok(self, send_donation_email):
        payment = Payment.objects.create(
            person=self.data["people"]["user1"],
            price=1000,
            type=DonsConfig.PAYMENT_TYPE,
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
        trans_uuid = str(uuid.uuid4()).replace("-", "")
        systempay_data = {
            "vads_trans_status": "AUTHORISED",
            "vads_order_id": SystemPayTransaction.objects.filter(payment=payment)
            .last()
            .pk,
            "vads_trans_uuid": trans_uuid,
            "vads_operation_type": "DEBIT",
        }
        systempay_data["signature"] = get_signature(
            systempay_data, settings.SYSTEMPAY_CERTIFICATE
        )
        res = self.client.post(reverse("system_pay:webhook"), systempay_data)
        self.assertEqual(res.status_code, 200)
        payment.refresh_from_db()
        self.assertEqual(payment.status, Payment.STATUS_COMPLETED)
        self.assertEqual(
            2, SystemPayTransaction.objects.filter(payment=payment).count()
        )

        trans_uuid = str(uuid.uuid4()).replace("-", "")
        systempay_data = {
            "vads_trans_status": "REFUSED",
            "vads_order_id": SystemPayTransaction.objects.filter(payment=payment)
            .first()
            .pk,
            "vads_trans_uuid": trans_uuid,
            "vads_operation_type": "DEBIT",
        }
        systempay_data["signature"] = get_signature(
            systempay_data, settings.SYSTEMPAY_CERTIFICATE
        )
        res = self.client.post(reverse("system_pay:webhook"), systempay_data)
        self.assertEqual(res.status_code, 200)
        payment.refresh_from_db()
        self.assertEqual(payment.status, Payment.STATUS_COMPLETED)
        self.assertEqual(
            2, SystemPayTransaction.objects.filter(payment=payment).count()
        )

    @mock.patch("agir.donations.views.send_donation_email")
    def test_test_transaction_on_canceled_payment(self, send_donation_email):
        payment = Payment.objects.create(
            person=self.data["people"]["user1"],
            price=1000,
            type=DonsConfig.PAYMENT_TYPE,
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
        trans_uuid = str(uuid.uuid4()).replace("-", "")
        systempay_data = {
            "vads_trans_status": "AUTHORISED",
            "vads_order_id": SystemPayTransaction.objects.filter(payment=payment)
            .last()
            .pk,
            "vads_trans_uuid": trans_uuid,
            "vads_operation_type": "DEBIT",
        }
        systempay_data["signature"] = get_signature(
            systempay_data, settings.SYSTEMPAY_CERTIFICATE
        )
        res = self.client.post(reverse("system_pay:webhook"), systempay_data)
        self.assertEqual(res.status_code, 200)
        payment.refresh_from_db()
        self.assertEqual(payment.status, Payment.STATUS_CANCELED)

    @mock.patch("agir.donations.views.send_donation_email")
    def test_test_subscription(self, send_donation_email):
        subscription = Subscription.objects.create(
            person=self.data["people"]["user1"],
            price=1000,
            type=DonsConfig.PAYMENT_TYPE,
            mode=SystemPayPaymentMode.id,
        )

        self.client.force_login(self.data["people"]["user1"].role)

        res = self.client.get(reverse("subscription_page", args=[subscription.pk]))
        self.assertContains(res, "vads")
        self.assertEqual(
            1, SystemPayTransaction.objects.filter(subscription=subscription).count()
        )

        self.client.logout()

        trans_id = (
            SystemPayTransaction.objects.filter(subscription=subscription).last().pk
        )
        trans_uuid = str(uuid.uuid4()).replace("-", "")
        systempay_data = {
            "vads_trans_status": "ACCEPTED",
            "vads_order_id": trans_id,
            "vads_trans_id": vads_trans_id(trans_id),
            "vads_trans_uuid": trans_uuid,
            "vads_operation_type": "DEBIT",
        }
        systempay_data["signature"] = get_signature(
            systempay_data, settings.SYSTEMPAY_CERTIFICATE
        )
        res = self.client.post(reverse("system_pay:webhook"), systempay_data)

        self.assertEqual(res.status_code, 200)
        subscription.refresh_from_db()
        self.assertEqual(subscription.status, Subscription.STATUS_COMPLETED)
        self.assertEqual(subscription.payments.all().count(), 0)

        trans_uuid = str(uuid.uuid4()).replace("-", "")
        systempay_data = {
            "vads_trans_status": "CAPTURED",
            "vads_order_id": trans_id,
            "vads_trans_id": vads_trans_id(
                trans_id + 10
            ),  # new transaction, created by systempay
            "vads_cust_id": str(subscription.person_id).replace("-", ""),
            "vads_amount": "1000",
            "vads_trans_uuid": trans_uuid,
            "vads_operation_type": "DEBIT",
        }
        systempay_data["signature"] = get_signature(
            systempay_data, settings.SYSTEMPAY_CERTIFICATE
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
        trans_uuid = str(uuid.uuid4()).replace("-", "")
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
