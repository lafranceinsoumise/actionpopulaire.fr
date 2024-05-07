from datetime import timedelta
from unittest import mock

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from agir.people.models import Person, PersonTag
from .models import Poll, PollOption, PollChoice
from .tasks import send_vote_confirmation_email


class PollModelTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_insoumise(
            email="participant@example.com", create_role=True
        )

    def test_can_make_choice(self):
        poll = Poll.objects.create(
            start=timezone.now(), end=timezone.now() + timedelta(days=1)
        )
        options = [
            PollOption.objects.create(poll=poll, description="Premier"),
            PollOption.objects.create(poll=poll, description="Deuxième"),
            PollOption.objects.create(poll=poll, description="Troisième"),
        ]
        poll.make_choice(
            self.person, {PollOption.DEFAULT_OPTION_GROUP_ID: [options[0].pk]}
        )
        choice = PollChoice.objects.first()
        self.assertEqual(choice.person, self.person)
        self.assertEqual(
            choice.selection, {PollOption.DEFAULT_OPTION_GROUP_ID: [str(options[0].pk)]}
        )

    def test_can_make_multiple_choices(self):
        poll = Poll.objects.create(
            start=timezone.now(), end=timezone.now() + timedelta(days=1)
        )
        options = [
            PollOption.objects.create(poll=poll, description="Premier"),
            PollOption.objects.create(poll=poll, description="Deuxième"),
            PollOption.objects.create(poll=poll, description="Troisième"),
        ]
        selected_options = [option.pk for option in options[:2]]
        poll.make_choice(
            self.person, {PollOption.DEFAULT_OPTION_GROUP_ID: selected_options}
        )
        choice = PollChoice.objects.first()
        self.assertEqual(choice.person, self.person)
        self.assertEqual(
            choice.selection,
            {
                PollOption.DEFAULT_OPTION_GROUP_ID: [
                    str(option_pk) for option_pk in selected_options
                ]
            },
        )

    def test_can_make_multiple_grouped_choices(self):
        poll = Poll.objects.create(
            start=timezone.now(), end=timezone.now() + timedelta(days=1)
        )
        options = [
            PollOption.objects.create(poll=poll, description="Premier"),
            PollOption.objects.create(
                poll=poll, description="Deuxième", option_group_id="another_choice"
            ),
            PollOption.objects.create(poll=poll, description="Troisième"),
        ]
        selected_options = [option.pk for option in options[:2]]
        poll.make_choice(
            self.person,
            {
                PollOption.DEFAULT_OPTION_GROUP_ID: selected_options[0:1],
                "another_choice": selected_options[1:2],
            },
        )
        choice = PollChoice.objects.first()
        self.assertEqual(choice.person, self.person)
        self.assertEqual(
            choice.selection,
            {
                PollOption.DEFAULT_OPTION_GROUP_ID: [str(options[0].pk)],
                "another_choice": [str(options[1].pk)],
            },
        )


class PollTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_insoumise(
            email="participant@example.com",
            created=timezone.now() + timedelta(days=-10),
            create_role=True,
        )
        self.client.force_login(self.person.role)

    def test_can_view_poll(self):
        poll = Poll.objects.create(
            title="title",
            description="description",
            start=timezone.now() + timedelta(hours=-1),
            end=timezone.now() + timedelta(days=1),
        )
        poll.tags.add(PersonTag.objects.create(label="test_tag"))
        _options = [
            PollOption.objects.create(poll=poll, description="Premier"),
            PollOption.objects.create(poll=poll, description="Deuxième"),
            PollOption.objects.create(poll=poll, description="Troisième"),
        ]

        res = self.client.get(reverse("participate_poll", args=[poll.pk]))

        self.assertContains(res, '<h2 class="headline">title</h2>')
        self.assertContains(res, "<p>description</p>")
        self.assertContains(res, "Premier")
        self.assertContains(res, "Deuxième")
        self.assertContains(res, "Troisième")

    def test_cannot_view_not_started_poll(self):
        poll = Poll.objects.create(
            title="title",
            description="description",
            start=timezone.now() + timedelta(hours=1),
            end=timezone.now() + timedelta(days=1),
        )
        _options = [
            PollOption.objects.create(poll=poll, description="Premier"),
            PollOption.objects.create(poll=poll, description="Deuxième"),
            PollOption.objects.create(poll=poll, description="Troisième"),
        ]
        res = self.client.get(reverse("participate_poll", args=[poll.pk]))
        self.assertEqual(res.status_code, 404)

    def test_cannot_view_finished_poll(self):
        poll = Poll.objects.create(
            title="title",
            description="description",
            start=timezone.now() + timedelta(days=-1, hours=-1),
            end=timezone.now() + timedelta(hours=-1),
        )
        _options = [
            PollOption.objects.create(poll=poll, description="Premier"),
            PollOption.objects.create(poll=poll, description="Deuxième"),
            PollOption.objects.create(poll=poll, description="Troisième"),
        ]
        res = self.client.get(reverse("participate_poll", args=[poll.pk]))
        self.assertRedirects(res, reverse("finished_poll"))

    def test_can_participate(self):
        poll = Poll.objects.create(
            title="title",
            description="description",
            start=timezone.now() + timedelta(hours=-1),
            end=timezone.now() + timedelta(days=1),
        )
        poll.tags.add(PersonTag.objects.create(label="test_tag"))
        options = [
            PollOption.objects.create(poll=poll, description="Premier"),
            PollOption.objects.create(poll=poll, description="Deuxième"),
            PollOption.objects.create(poll=poll, description="Troisième"),
        ]
        res = self.client.post(
            reverse("participate_poll", args=[poll.pk]),
            data={
                PollOption.DEFAULT_OPTION_GROUP_ID: [
                    str(options[0].pk),
                    str(options[2].pk),
                ]
            },
        )
        self.assertRedirects(res, reverse("participate_poll", args=[poll.pk]))
        choice = PollChoice.objects.first()
        self.assertIn("test_tag", [str(tag) for tag in self.person.tags.all()])
        self.assertEqual(choice.person, self.person)
        self.assertCountEqual(
            choice.selection.get(PollOption.DEFAULT_OPTION_GROUP_ID),
            [str(options[0].pk), str(options[2].pk)],
        )

    def test_cannot_participate_if_just_registered(self):
        person = Person.objects.create_insoumise(
            email="just_created@example.com", create_role=True
        )
        self.client.force_login(person.role)
        poll = Poll.objects.create(
            title="title",
            description="description",
            start=timezone.now() + timedelta(hours=-1),
            end=timezone.now() + timedelta(days=1),
        )
        options = [
            PollOption.objects.create(poll=poll, description="Premier"),
            PollOption.objects.create(poll=poll, description="Deuxième"),
            PollOption.objects.create(poll=poll, description="Troisième"),
        ]
        res = self.client.post(
            reverse("participate_poll", args=[poll.pk]),
            data={
                PollOption.DEFAULT_OPTION_GROUP_ID: [
                    str(options[0].pk),
                    str(options[2].pk),
                ]
            },
        )
        self.assertContains(res, "trop récemment", status_code=403)

    def test_cannot_participate_twice(self):
        poll = Poll.objects.create(
            title="title",
            description="description",
            start=timezone.now() + timedelta(hours=-1),
            end=timezone.now() + timedelta(days=1),
        )
        options = [
            PollOption.objects.create(poll=poll, description="Premier"),
            PollOption.objects.create(poll=poll, description="Deuxième"),
            PollOption.objects.create(poll=poll, description="Troisième"),
        ]
        res = self.client.post(
            reverse("participate_poll", args=[poll.pk]),
            data={
                PollOption.DEFAULT_OPTION_GROUP_ID: [
                    str(options[0].pk),
                    str(options[2].pk),
                ]
            },
        )
        self.assertRedirects(res, reverse("participate_poll", args=[poll.pk]))
        res = self.client.get(reverse("participate_poll", args=[poll.pk]))
        self.assertContains(res, "Vous avez bien participé")
        res = self.client.post(
            reverse("participate_poll", args=[poll.pk]),
            data={
                PollOption.DEFAULT_OPTION_GROUP_ID: [
                    str(options[0].pk),
                    str(options[2].pk),
                ]
            },
        )
        self.assertContains(res, "déjà participé", status_code=403)

    def test_must_respect_min_and_max_option_rule(self):
        poll = Poll.objects.create(
            title="title",
            description="description",
            start=timezone.now() + timedelta(hours=-1),
            end=timezone.now() + timedelta(days=1),
            rules={"min_options": 2, "max_options": 3},
        )
        options = [
            PollOption.objects.create(poll=poll, description="Premier"),
            PollOption.objects.create(poll=poll, description="Deuxième"),
            PollOption.objects.create(poll=poll, description="Troisième"),
            PollOption.objects.create(poll=poll, description="Quatrième"),
        ]
        res = self.client.post(
            reverse("participate_poll", args=[poll.pk]),
            data={PollOption.DEFAULT_OPTION_GROUP_ID: [str(options[0].pk)]},
        )
        self.assertContains(res, "minimum")
        res = self.client.post(
            reverse("participate_poll", args=[poll.pk]),
            data={
                PollOption.DEFAULT_OPTION_GROUP_ID: [
                    str(options[0].pk),
                    str(options[1].pk),
                    str(options[2].pk),
                    str(options[3].pk),
                ]
            },
        )
        self.assertContains(res, "maximum")

    def test_must_respect_fixed_option_limit_rule(self):
        poll = Poll.objects.create(
            title="title",
            description="description",
            start=timezone.now() + timedelta(hours=-1),
            end=timezone.now() + timedelta(days=1),
            rules={"options": 2},
        )
        options = [
            PollOption.objects.create(poll=poll, description="Premier"),
            PollOption.objects.create(poll=poll, description="Deuxième"),
            PollOption.objects.create(poll=poll, description="Troisième"),
        ]
        res = self.client.post(
            reverse("participate_poll", args=[poll.pk]),
            data={PollOption.DEFAULT_OPTION_GROUP_ID: [str(options[0].pk)]},
        )
        self.assertContains(res, "exactement")
        res = self.client.post(
            reverse("participate_poll", args=[poll.pk]),
            data={
                PollOption.DEFAULT_OPTION_GROUP_ID: [
                    str(options[0].pk),
                    str(options[1].pk),
                    str(options[2].pk),
                ]
            },
        )
        self.assertContains(res, "exactement")

    def test_redirects_if_not_verified(self):
        poll = Poll.objects.create(
            title="title",
            description="description",
            start=timezone.now() + timedelta(hours=-1),
            end=timezone.now() + timedelta(days=1),
            rules={"verified_user": True},
        )
        _options = [
            PollOption.objects.create(poll=poll, description="Premier"),
            PollOption.objects.create(poll=poll, description="Deuxième"),
            PollOption.objects.create(poll=poll, description="Troisième"),
        ]
        poll_url = reverse("participate_poll", args=[poll.pk])
        res = self.client.get(poll_url)
        self.assertRedirects(res, reverse("send_validation_sms") + "?next=" + poll_url)

    def test_cannot_post_if_not_verified(self):
        poll = Poll.objects.create(
            title="title",
            description="description",
            start=timezone.now() + timedelta(hours=-1),
            end=timezone.now() + timedelta(days=1),
            rules={"verified_user": True},
        )
        options = [
            PollOption.objects.create(poll=poll, description="Premier"),
            PollOption.objects.create(poll=poll, description="Deuxième"),
            PollOption.objects.create(poll=poll, description="Troisième"),
        ]
        res = self.client.post(
            reverse("participate_poll", args=[poll.pk]),
            data={
                PollOption.DEFAULT_OPTION_GROUP_ID: [
                    str(options[0].pk),
                    str(options[1].pk),
                    str(options[2].pk),
                ]
            },
        )
        self.assertEqual(res.status_code, 403)

    @mock.patch("agir.polls.views.send_vote_confirmation_email")
    def test_send_email_by_default(
        self,
        send_vote_confirmation_email,
    ):
        poll = Poll.objects.create(
            start=timezone.now(),
            end=timezone.now() + timedelta(days=1),
            rules={"options": 1},
        )
        options = [
            PollOption.objects.create(poll=poll, description="Premier"),
            PollOption.objects.create(poll=poll, description="Deuxième"),
        ]
        res = self.client.post(
            reverse("participate_poll", args=[poll.id]),
            data={PollOption.DEFAULT_OPTION_GROUP_ID: options[0].id},
        )
        self.assertRedirects(res, reverse("participate_poll", args=[poll.id]))
        send_vote_confirmation_email.delay.assert_called_once()

    @mock.patch("agir.polls.views.send_vote_confirmation_email")
    def test_send_email_when_enabled(
        self,
        send_vote_confirmation_email,
    ):
        poll = Poll.objects.create(
            start=timezone.now(),
            end=timezone.now() + timedelta(days=1),
            rules={"options": 1, "confirmation_email": True},
        )
        options = [
            PollOption.objects.create(poll=poll, description="Premier"),
            PollOption.objects.create(poll=poll, description="Deuxième"),
        ]
        res = self.client.post(
            reverse("participate_poll", args=[poll.id]),
            data={PollOption.DEFAULT_OPTION_GROUP_ID: options[0].id},
        )
        self.assertRedirects(res, reverse("participate_poll", args=[poll.id]))
        send_vote_confirmation_email.delay.assert_called_once()

    @mock.patch("agir.polls.views.send_vote_confirmation_email")
    def test_do_not_send_email_when_disabled(
        self,
        send_vote_confirmation_email,
    ):
        poll = Poll.objects.create(
            start=timezone.now(),
            end=timezone.now() + timedelta(days=1),
            rules={"options": 1, "confirmation_email": False},
        )
        options = [
            PollOption.objects.create(poll=poll, description="Premier"),
            PollOption.objects.create(poll=poll, description="Deuxième"),
        ]
        res = self.client.post(
            reverse("participate_poll", args=[poll.id]),
            data={PollOption.DEFAULT_OPTION_GROUP_ID: options[0].id},
        )
        self.assertRedirects(res, reverse("participate_poll", args=[poll.id]))
        send_vote_confirmation_email.delay.assert_not_called()

    def test_redirect_to_configured_url(self):
        poll = Poll.objects.create(
            start=timezone.now(),
            end=timezone.now() + timedelta(days=1),
            rules={"options": 1, "success_url": "https://superduperwebsite.fr/"},
        )
        options = [
            PollOption.objects.create(poll=poll, description="Premier"),
            PollOption.objects.create(poll=poll, description="Deuxième"),
        ]
        res = self.client.post(
            reverse("participate_poll", args=[poll.id]),
            data={PollOption.DEFAULT_OPTION_GROUP_ID: options[0].id},
        )
        choice = poll.pollchoice_set.first()
        self.assertRedirects(
            res,
            f"https://superduperwebsite.fr/?anonymous_id={choice.anonymous_id}",
            fetch_redirect_response=False,
        )

    def test_must_can_override_rules_for_option_group(self):
        poll = Poll.objects.create(
            title="title",
            description="description",
            start=timezone.now() + timedelta(hours=-1),
            end=timezone.now() + timedelta(days=1),
            rules={
                "max_options": 1,
                "option_groups": {
                    "B": {
                        "label": "Groupe B",
                        "max_options": None,
                    }
                },
            },
        )
        options = [
            PollOption.objects.create(
                poll=poll, description="Premier", option_group_id="A"
            ),
            PollOption.objects.create(
                poll=poll, description="Deuxième", option_group_id="A"
            ),
            PollOption.objects.create(
                poll=poll, description="Troisième", option_group_id="B"
            ),
            PollOption.objects.create(
                poll=poll, description="Quatrième", option_group_id="B"
            ),
        ]
        poll_url = reverse("participate_poll", args=[poll.pk])
        res = self.client.get(poll_url)
        self.assertContains(res, "Groupe B")
        res = self.client.post(
            reverse("participate_poll", args=[poll.pk]),
            data={
                "A": [str(options[0].pk), str(options[1].pk)],
                "B": [str(options[2].pk), str(options[3].pk)],
            },
        )
        self.assertContains(res, "maximum")
        self.assertIsNone(PollChoice.objects.first())
        self.client.post(
            reverse("participate_poll", args=[poll.pk]),
            data={
                "A": [str(options[0].pk)],
                "B": [str(options[2].pk), str(options[3].pk)],
            },
        )
        choice = PollChoice.objects.first()
        self.assertEqual(choice.person, self.person)
        self.assertCountEqual(choice.selection.get("A"), [str(options[0].pk)])
        self.assertCountEqual(
            choice.selection.get("B"), [str(options[2].pk), str(options[3].pk)]
        )
