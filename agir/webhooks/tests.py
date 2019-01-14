import json
import base64
from rest_framework.test import APITestCase
from django.utils import timezone
from agir.people.models import Person, PersonEmail


class WebhookTestCase(APITestCase):
    def setUp(self):
        self.new_bounced_person = Person.objects.create_person(email="new@bounce.com")

        self.old_bounced_person = Person.objects.create_person(
            email="old@bounce.com", created=timezone.now() - timezone.timedelta(hours=2)
        )
        self.old_bounced_person.add_email("other_old@bounce.com")

        self.sendgrid_payload = [
            {"email": "new@bounce.com", "event": "bounce"},
            {"email": "old@bounce.com", "event": "bounce"},
        ]

        self.sendgrid_payload2 = [{"email": "other_old@bounce.com", "event": "bounce"}]

        self.ses_payload = r"""{
                  "Type" : "Notification",
                  "Message" : "{\"notificationType\":\"Bounce\",\"bounce\":{\"bounceType\":\"Permanent\",\"bounceSubType\":\"General\",\"bouncedRecipients\":[{\"emailAddress\":\"old@bounce.com\",\"action\":\"failed\",\"status\":\"5.1.1\",\"diagnosticCode\":\"smtp; 550 5.1.1 <old@bounce.com>: Recipient address rejected: User unknown in virtual mailbox table\"}]},\"mail\":{\"destination\":[\"old@bounce.com\"]}}"
                }"""

    def test_sendgrid_bounce_users(self):
        response = self.client.post(
            "/webhooks/sendgrid_bounce",
            self.sendgrid_payload,
            format="json",
            HTTP_AUTHORIZATION="Basic "
            + (base64.b64encode(b"fi:prout").decode("utf-8")),
        )
        self.assertEqual(response.status_code, 202)
        self.assertEqual(True, Person.objects.get(email="old@bounce.com").bounced)
        with self.assertRaises(Person.DoesNotExist):
            Person.objects.get(email="new@bounce.com")

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

    def test_amazon_bounce_old_user(self):
        response = self.client.post(
            "/webhooks/ses_bounce",
            self.ses_payload,
            content_type="text/plain; charset=UTF-8",
            HTTP_AUTHORIZATION="Basic "
            + (base64.b64encode(b"fi:prout").decode("utf-8")),
        )
        self.assertEqual(response.status_code, 202)
        self.assertEqual(True, Person.objects.get(email="old@bounce.com").bounced)

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
        self.assertEqual(False, Person.objects.get(email="old@bounce.com").bounced)
        self.assertEqual(
            True, Person.objects.get(email="old@bounce.com").emails.all()[1].bounced
        )
