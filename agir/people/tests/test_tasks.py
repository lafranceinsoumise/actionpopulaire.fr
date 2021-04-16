from django.test import TestCase
from django.core import mail

from agir.people.models import Person
from agir.people import tasks


class PeopleTasksTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_insoumise("me@me.org")
        self.person.ensure_role_exists()

    def test_welcome_mail(self):
        tasks.send_welcome_mail(self.person.pk, type="LFI")

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].recipients(), [self.person.email])

    def test_unsubscribe_mail(self):
        tasks.send_unsubscribe_email(self.person.pk)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].recipients(), [self.person.email])

    def test_user_no_role_dont_receive_mail(self):
        self.person.role = None
        tasks.send_welcome_mail(self.person.pk, type="LFI")

        self.assertEqual(len(mail.outbox), 0)

    def test_inactive_user_dont_receive_mail(self):
        self.person.role.is_active = False
        tasks.send_welcome_mail(self.person.pk, type="LFI")

        self.assertEqual(len(mail.outbox), 0)
