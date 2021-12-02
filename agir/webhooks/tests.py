import json
import base64
from rest_framework.test import APITestCase
from django.utils import timezone
from agir.people.models import Person, PersonEmail


class WebhookTestCase(APITestCase):
    def setUp(self):
        self.person = Person.objects.create_insoumise(
            email="primary@bounce.com",
            created=timezone.now() - timezone.timedelta(hours=2),
        )
        self.person.add_email("secondary@bounce.com")

        self.sendgrid_payload = [
            {"email": "primary@bounce.com", "event": "bounce"},
        ]

        self.sendgrid_payload2 = [
            {"email": "secondary@bounce.com", "event": "bounce"},
        ]

        self.ses_payload = r"""{
                  "Type" : "Notification",
                  "Message" : "{\"notificationType\":\"Bounce\",\"bounce\":{\"bounceType\":\"Permanent\",\"bounceSubType\":\"General\",\"bouncedRecipients\":[{\"emailAddress\":\"primary@bounce.com\",\"action\":\"failed\",\"status\":\"5.1.1\",\"diagnosticCode\":\"smtp; 550 5.1.1 <primary@bounce.com>: Recipient address rejected: User unknown in virtual mailbox table\"}]},\"mail\":{\"destination\":[\"primary@bounce.com\"]}}"
                }"""

    def test_sendgrid_bounce(self):
        response = self.client.post(
            "/webhooks/sendgrid_bounce",
            self.sendgrid_payload,
            format="json",
            HTTP_AUTHORIZATION="Basic "
            + (base64.b64encode(b"fi:prout").decode("utf-8")),
        )
        self.assertEqual(response.status_code, 202)
        self.person.refresh_from_db()
        self.assertEqual(
            "secondary@bounce.com",
            self.person.email,
        )
        self.assertTrue(PersonEmail.objects.get(address="primary@bounce.com").bounced)

    def test_sendgrid_auth(self):
        response = self.client.post(
            "/webhooks/sendgrid_bounce",
            self.sendgrid_payload,
            format="json",
            HTTP_AUTHORIZATION="Basic "
            + (base64.b64encode(b"fi:burp").decode("utf-8")),
        )
        self.assertEqual(response.status_code, 401)
        response = self.client.post(
            "/webhooks/sendgrid_bounce", self.sendgrid_payload, format="json"
        )
        self.assertEqual(response.status_code, 401)

    def test_amazon_bounce(self):
        response = self.client.post(
            "/webhooks/ses_bounce",
            self.ses_payload,
            content_type="text/plain; charset=UTF-8",
            HTTP_AUTHORIZATION="Basic "
            + (base64.b64encode(b"fi:prout").decode("utf-8")),
        )
        self.assertEqual(response.status_code, 202)
        self.person.refresh_from_db()
        self.assertEqual(
            "secondary@bounce.com",
            self.person.email,
        )
        self.assertTrue(PersonEmail.objects.get(address="primary@bounce.com").bounced)

    def test_amazon_auth(self):
        response = self.client.post(
            "/webhooks/ses_bounce",
            self.ses_payload,
            content_type="text/plain; charset=UTF-8",
            HTTP_AUTHORIZATION="Basic "
            + (base64.b64encode(b"fi:burp").decode("utf-8")),
        )
        self.assertEqual(response.status_code, 401)
        response = self.client.post("/webhooks/ses_bounce", self.ses_payload)
        self.assertEqual(response.status_code, 401)

    def test_bounce_secondary_email(self):
        response = self.client.post(
            "/webhooks/sendgrid_bounce",
            self.sendgrid_payload2,
            format="json",
            HTTP_AUTHORIZATION="Basic "
            + (base64.b64encode(b"fi:prout").decode("utf-8")),
        )
        self.assertEqual(response.status_code, 202)
        self.person.refresh_from_db()
        self.assertFalse(PersonEmail.objects.get(address="primary@bounce.com").bounced)
        self.assertTrue(PersonEmail.objects.get(address="secondary@bounce.com").bounced)
