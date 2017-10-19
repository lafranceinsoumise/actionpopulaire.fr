import json
import base64
from rest_framework.test import APITestCase
from django.utils import timezone
from people.models import Person, PersonEmail


class WebhookTestCase(APITestCase):
    def setUp(self):
        self.new_bounced_person = Person.objects.create_person(
            email='new@bounce.com',
            created=timezone.now()
        )

        self.old_bounced_person = Person.objects.create_person(
            email='old@bounce.com',
            created=timezone.now() - timezone.timedelta(hours=2)
        )

        self.old_bounced_person.add_email('other_old@bounce.com')

        self.sendgrid_payload = [
            {
                "email": "new@bounce.com",
                "event": "bounce"
            },
            {
                "email": "old@bounce.com",
                "event": "bounce"
            }
        ]

        self.sendgrid_payload2 = [
            {
                "email": "other_old@bounce.com",
                "event": "bounce"
            }
        ]

        self.ses_payload = r'''{
              "Type" : "Notification",
              "MessageId" : "7ba9da19-da05-55b5-8074-8bc6e50cfdf1",
              "TopicArn" : "arn:aws:sns:eu-west-1:106475418133:jlm2017-newsletter-notification",
              "Message" : "{\"notificationType\":\"Bounce\",\"bounce\":{\"bounceType\":\"Permanent\",\"bounceSubType\":\"General\",\"bouncedRecipients\":[{\"emailAddress\":\"old@bounce.com\",\"action\":\"failed\",\"status\":\"5.1.1\",\"diagnosticCode\":\"smtp; 550 5.1.1 <old@bounce.com>: Recipient address rejected: User unknown in virtual mailbox table\"}],\"timestamp\":\"2017-07-11T21:02:01.056Z\",\"feedbackId\":\"0102015d3375711d-abd3f429-32f0-4ebe-81b9-f765e95ff3ba-000000\",\"remoteMtaIp\":\"217.70.184.6\",\"reportingMTA\":\"dsn; a6-144.smtp-out.eu-west-1.amazonses.com\"},\"mail\":{\"timestamp\":\"2017-07-11T21:01:59.000Z\",\"source\":\"nepasrepondre@lafranceinsoumise.fr\",\"sourceArn\":\"arn:aws:ses:eu-west-1:106475418133:identity/lafranceinsoumise.fr\",\"sourceIp\":\"163.172.170.222\",\"sendingAccountId\":\"106475418133\",\"messageId\":\"0102015d33756cb0-9ef9f3ed-65bb-4054-bd09-c3fc71aa19ba-000000\",\"destination\":[\"old@bounce.com\"]}}"
            }'''

    def test_sendgrid_bounce_users(self):
        response = self.client.post('/webhooks/sendgrid_bounce', self.sendgrid_payload, format='json',
            HTTP_AUTHORIZATION='Basic ' + (base64.b64encode(b'fi:prout').decode('utf-8')))
        self.assertEqual(response.status_code, 202)
        self.assertEqual(True, Person.objects.get(email='old@bounce.com').bounced)
        with self.assertRaises(Person.DoesNotExist):
            Person.objects.get(email='new@bounce.com')

    def test_sendgrid_auth(self):
        response = self.client.post('/webhooks/sendgrid_bounce', self.sendgrid_payload, format='json',
            HTTP_AUTHORIZATION='Basic ' + (base64.b64encode(b'fi:burp').decode('utf-8')))
        self.assertEqual(response.status_code, 401)
        response = self.client.post('/webhooks/sendgrid_bounce', self.sendgrid_payload, format='json')
        self.assertEqual(response.status_code, 401)

    def test_amazon_bounce_old_user(self):
        response = self.client.post('/webhooks/ses_bounce', self.ses_payload, content_type='text/plain; charset=UTF-8',
            HTTP_AUTHORIZATION='Basic ' + (base64.b64encode(b'fi:prout').decode('utf-8')))
        self.assertEqual(response.status_code, 202)
        self.assertEqual(True, Person.objects.get(email='old@bounce.com').bounced)

    def test_amazon_auth(self):
        response = self.client.post('/webhooks/ses_bounce', self.ses_payload, content_type='text/plain; charset=UTF-8',
            HTTP_AUTHORIZATION='Basic ' + (base64.b64encode(b'fi:burp').decode('utf-8')))
        self.assertEqual(response.status_code, 401)
        response = self.client.post('/webhooks/ses_bounce', self.ses_payload)
        self.assertEqual(response.status_code, 401)

    def test_bounce_secondary_email(self):
        response = self.client.post('/webhooks/sendgrid_bounce', self.sendgrid_payload2, format='json',
            HTTP_AUTHORIZATION='Basic ' + (base64.b64encode(b'fi:prout').decode('utf-8')))
        self.assertEqual(response.status_code, 202)
        self.assertEqual(False, Person.objects.get(email='old@bounce.com').bounced)
        self.assertEqual(True, Person.objects.get(email='old@bounce.com').emails.all()[1].bounced)
