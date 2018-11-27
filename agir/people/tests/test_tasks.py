from django.test import TestCase
from django.core import mail

from agir.people.models import Person
from agir.people import tasks


class PeopleTasksTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_person("me@me.org")

    def test_welcome_mail(self):
        tasks.send_welcome_mail(self.person.pk)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].recipients(), [self.person.email])

    def test_unsubscribe_mail(self):
        tasks.send_unsubscribe_email(self.person.pk)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].recipients(), [self.person.email])
