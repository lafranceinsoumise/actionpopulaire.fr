from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from agir.cagnottes.models import Cagnotte
from agir.payments import payment_modes
from agir.payments.models import Payment
from agir.people.models import Person


class CagnotteTestCase(TestCase):
    def setUp(self):
        self.p1 = Person.objects.create_2022("test@test.com", create_role=True)

        self.cagnotte = Cagnotte.objects.create(
            nom="Cagnotte",
            slug="super_cagnotte",
        )

        self.donation_information_payload = {
            "nationality": "FR",
            "first_name": "Marc",
            "last_name": "Frank",
            "location_address1": "4 rue de Chaume",
            "location_address2": "",
            "location_zip": "33000",
            "location_city": "Bordeaux",
            "location_country": "FR",
            "contact_phone": "+33645789845",
            "amount": "20000",
            "payment_mode": payment_modes.DEFAULT_MODE,
            "civilite": "F",
            "declaration": "Y",
        }

        self.information_url = reverse(
            "cagnottes:personal_information", kwargs={"slug": self.cagnotte.slug}
        )

    def test_create_payment(self):
        self.client.force_login(self.p1.role)
        url = f"{self.information_url}?amount=1000"

        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

        res = self.client.post(url, data=self.donation_information_payload)
        self.assertEqual(res.status_code, status.HTTP_302_FOUND)

        payment = Payment.objects.get()
        self.assertEqual(payment.type, "don_cagnotte")
        self.assertEqual(payment.meta["cagnotte"], self.cagnotte.id)

        self.assertRedirects(res, payment.get_payment_url())
