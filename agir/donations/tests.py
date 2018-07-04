from django.test import TestCase
from django.urls import reverse
from unittest import mock

from agir.payments.actions import complete_payment
from .views import notification_listener as donation_notification_listener
from ..people.models import Person
from ..payments.models import Payment


class DonationTestCase(TestCase):
    def setUp(self):
        self.p1 = Person.objects.create_person('test@test.com')

        self.donation_information_payload = {
            'amount': '20000',
            'declaration': 'Y',
            'nationality': 'FR',
            'first_name': 'Marc',
            'last_name': 'Frank',
            'location_address1': '4 rue de Chaume',
            'location_address2': '',
            'location_zip': '33000',
            'location_city': 'Bordeaux',
            'location_country': 'FR',
            'contact_phone': '06 45 78 98 45'
        }

    @mock.patch('agir.donations.views.send_donation_email')
    def test_can_donate_while_logged_in(self, send_donation_email):
        self.client.force_login(self.p1.role)
        amount_url = reverse('donation_amount')
        information_url = reverse('donation_information')

        res = self.client.get(amount_url)
        self.assertEqual(res.status_code, 200)

        res = self.client.post(amount_url, {'amount': '200'})
        self.assertRedirects(res, information_url)

        res = self.client.get(information_url)
        self.assertEqual(res.status_code, 200)

        res = self.client.post(information_url, self.donation_information_payload)
        # no other payment
        payment = Payment.objects.get()
        self.assertRedirects(res, reverse('payment_page', args=(payment.pk,)))

        res = self.client.get(reverse('payment_return', args=(payment.pk,)))
        self.assertEqual(res.status_code, 200)

        self.p1.refresh_from_db()

        # assert fields have been saved on model
        for f in ['first_name', 'last_name', 'location_address1', 'location_address2', 'location_zip', 'location_city',
                  'location_country']:
            self.assertEqual(getattr(self.p1, f), self.donation_information_payload[f])



        # fake systempay webhook
        complete_payment(payment)
        donation_notification_listener(payment)
        send_donation_email.delay.assert_called_once()

    def test_cannot_donate_without_required_fields(self):
        information_url = reverse('donation_information')

        res = self.client.post(reverse('donation_amount'), {'amount': '200'})
        self.assertRedirects(res, information_url)

        required_fields = [
            'declaration', 'nationality', 'first_name', 'last_name', 'location_address1', 'location_zip',
            'location_city', 'location_country'
        ]

        for f in required_fields:
            d = self.donation_information_payload.copy()
            del d[f]

            res = self.client.post(information_url, d)
            self.assertEqual(res.status_code, 200, msg="Should not redirect when field '%s' missing" % f)

    def test_cannot_donate_without_asserting_fiscal_residency_when_foreigner(self):
        self.client.force_login(self.p1.role)

        information_url = reverse('donation_information')

        res = self.client.post(reverse('donation_amount'), {'amount': '200'})
        self.assertRedirects(res, information_url)

        self.donation_information_payload['nationality'] = 'ES'

        res = self.client.post(information_url, self.donation_information_payload)
        self.assertEqual(res.status_code, 200)

        self.donation_information_payload['fiscal_resident'] = 'Y'
        res = self.client.post(information_url, self.donation_information_payload)
        payment = Payment.objects.get()
        self.assertRedirects(res, reverse('payment_page', args=[payment.pk]))

    def test_update_person_when_using_existing_address(self):
        information_url = reverse('donation_information')

        res = self.client.post(reverse('donation_amount'), {'amount': '200'})
        self.assertRedirects(res, information_url)

        self.donation_information_payload['email'] = self.p1.email
        res = self.client.post(information_url, self.donation_information_payload)
        payment = Payment.objects.get()
        self.assertRedirects(res, reverse('payment_page', args=[payment.pk]))

        self.p1.refresh_from_db()

        # assert fields have been saved on model
        for f in ['first_name', 'last_name', 'location_address1', 'location_address2', 'location_zip', 'location_city',
                  'location_country']:
            self.assertEqual(getattr(self.p1, f), self.donation_information_payload[f])

    def test_create_person_when_using_new_address(self):
        information_url = reverse('donation_information')

        res = self.client.post(reverse('donation_amount'), {'amount': '200'})
        self.assertRedirects(res, information_url)

        self.donation_information_payload['email'] = 'test2@test.com'
        res = self.client.post(information_url, self.donation_information_payload)
        payment = Payment.objects.get()
        self.assertRedirects(res, reverse('payment_page', args=[payment.pk]))

        p2 = Person.objects.exclude(pk=self.p1.pk).get()
        # assert fields have been saved on model
        for f in ['first_name', 'last_name', 'location_address1', 'location_address2', 'location_zip', 'location_city',
                  'location_country', 'email']:
            self.assertEqual(getattr(p2, f), self.donation_information_payload[f])
