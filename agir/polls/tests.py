from datetime import timedelta
from functools import partial
from unittest import mock

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from agir.people.models import Person
from .models import Poll, PollOption, PollChoice
from .tasks import send_vote_confirmation_email


class PollModelTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_insoumise(
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


class PollViewTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_insoumise(
            email="participant@example.com", create_role=True
        )
        self.poll = Poll.objects.create(
            start=timezone.now(),
            end=timezone.now() + timedelta(days=1),
            rules={"options": 1},
        )
        self.option1 = PollOption.objects.create(poll=self.poll, description="Premier")
        self.option2 = PollOption.objects.create(poll=self.poll, description="Deuxième")
        self.client.force_login(self.person.role)

    @mock.patch("django.db.transaction.on_commit")
    def test_send_email_by_default(
        self,
        on_commit,
    ):
        res = self.client.post(
            reverse("participate_poll", args=[self.poll.id]),
            data={"choice": self.option1.id},
        )

        self.assertRedirects(res, reverse("participate_poll", args=[self.poll.id]))

        on_commit.assert_called_once()
        cb = on_commit.call_args[0][0]
        self.assertIsInstance(cb, partial)
        self.assertEqual(cb.func, send_vote_confirmation_email.delay)

    @mock.patch("django.db.transaction.on_commit")
    def test_send_email_when_enabled(
        self,
        on_commit,
    ):
        self.poll.rules["confirmation_email"] = True
        self.poll.save()

        res = self.client.post(
            reverse("participate_poll", args=[self.poll.id]),
            data={"choice": self.option1.id},
        )

        self.assertRedirects(res, reverse("participate_poll", args=[self.poll.id]))

        on_commit.assert_called_once()
        cb = on_commit.call_args[0][0]
        self.assertIsInstance(cb, partial)
        self.assertEqual(cb.func, send_vote_confirmation_email.delay)

    @mock.patch("django.db.transaction.on_commit")
    def test_do_not_send_email_when_disabled(
        self,
        on_commit,
    ):
        self.poll.rules["confirmation_email"] = False
        self.poll.save()

        res = self.client.post(
            reverse("participate_poll", args=[self.poll.id]),
            data={"choice": self.option1.id},
        )

        self.assertRedirects(res, reverse("participate_poll", args=[self.poll.id]))

        on_commit.assert_not_called()

    def test_redirect_to_configured_url(self):
        self.poll.rules["success_url"] = "https://superduperwebsite.fr/"
        self.poll.save()

        res = self.client.post(
            reverse("participate_poll", args=[self.poll.id]),
            data={"choice": self.option1.id},
        )
        choice = self.poll.pollchoice_set.first()
        self.assertRedirects(
            res,
            f"https://superduperwebsite.fr/?anonymous_id={choice.anonymous_id}",
            fetch_redirect_response=False,
        )
