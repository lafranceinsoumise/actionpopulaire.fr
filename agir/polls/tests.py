from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from agir.people.models import Person
from .models import Poll, PollOption, PollChoice


class PollTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_person(
            email="participant@example.com", create_role=True
        )
        self.poll = Poll.objects.create(
            start=timezone.now(), end=timezone.now() + timedelta(days=1)
        )
        PollOption.objects.create(poll=self.poll, description="Premier")
        PollOption.objects.create(poll=self.poll, description="Deuxième")
        PollOption.objects.create(poll=self.poll, description="Troisième")

    def test_can_make_choice(self):
        option = self.poll.options.all()[0]
        self.poll.make_choice(self.person, [option])

        choice = PollChoice.objects.first()
        self.assertEqual(choice.person, self.person)
        self.assertEqual(choice.selection, [str(option.pk)])

    def test_can_make_multiple_choice(self):
        options = list(self.poll.options.all()[0:2])
        self.poll.make_choice(self.person, options)

        choice = PollChoice.objects.first()
        self.assertEqual(choice.person, self.person)
        self.assertEqual(choice.selection, [str(option.pk) for option in options])
