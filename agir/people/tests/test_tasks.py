from django.test import TestCase
from django.core import mail

from agir.people.models import Person
from agir.people import tasks


class PeopleTasksTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_insoumise("me@me.org", create_role=True)

    def test_welcome_mail(self):
        tasks.send_welcome_mail(self.person.pk, type="LFI")

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].recipients(), [self.person.email])

    def test_unsubscribe_mail(self):
        tasks.send_unsubscribe_email(self.person.pk)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].recipients(), [self.person.email])

    def test_user_no_role_dont_receive_mail(self):
        no_role_person = Person.objects.create_insoumise("norole@me.org")
        no_role_person.role = None
        self.person.save()
        tasks.send_welcome_mail(no_role_person.pk, type="LFI")

        self.assertEqual(len(mail.outbox), 0)

    def test_inactive_user_dont_receive_mail(self):
        person = Person.objects.create_insoumise(
            "inactiverole@me.org", create_role=True
        )
        person.role.is_active = False
        person.role.save()
        tasks.send_welcome_mail(person.pk, type="LFI")

        self.assertEqual(len(mail.outbox), 0)
