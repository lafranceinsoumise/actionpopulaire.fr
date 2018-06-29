from django.test import TestCase
from django.urls import reverse
from unittest import mock

from agir.donations.apps import DonsConfig
from agir.lib.tests.mixins import FakeDataMixin
from agir.payments.models import Payment
from agir.system_pay import SystemPayPaymentMode
from agir.system_pay.crypto import get_signature
from agir.system_pay.models import SystemPayTransaction


class WebhookTestCase(FakeDataMixin, TestCase):
    @mock.patch('agir.donations.views.send_donation_email')
    def test_transaction_ok(self, send_donation_email):
        payment = Payment.objects.create(
            person=self.data['people']['user1'],
            price=1000,
            type=DonsConfig.PAYMENT_TYPE,
            mode=SystemPayPaymentMode.id
        )

        self.client.force_login(self.data['people']['user1'].role)

        res = self.client.get(reverse('payment_page', args=[payment.pk]))
        self.assertContains(res, "vads")
        self.assertEqual(1, SystemPayTransaction.objects.filter(payment=payment).count())

        res = self.client.get(reverse('payment_retry', args=[payment.pk]))
        self.assertContains(res, "vads")
        self.assertEqual(2 , SystemPayTransaction.objects.filter(payment=payment).count())

        self.client.logout()
        systempay_data = {
            'vads_trans_status': 'AUTHORISED',
            'vads_order_id': SystemPayTransaction.objects.filter(payment=payment).last().pk
        }
        systempay_data['signature'] = get_signature(systempay_data)
        res = self.client.post(reverse('system_pay:webhook'), systempay_data)
        self.assertEqual(res.status_code, 200)
        payment.refresh_from_db()
        self.assertEqual(payment.status, Payment.STATUS_COMPLETED)

        systempay_data = {
            'vads_trans_status': 'REFUSED',
            'vads_order_id': SystemPayTransaction.objects.filter(payment=payment).first().pk
        }
        systempay_data['signature'] = get_signature(systempay_data)
        self.assertEqual(res.status_code, 200)
        payment.refresh_from_db()
        self.assertEqual(payment.status, Payment.STATUS_COMPLETED)
