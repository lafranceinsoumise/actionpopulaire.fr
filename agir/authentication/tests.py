import uuid
from unittest import mock

import re
from django.contrib.auth import get_user
from django.core import mail
from django.http import QueryDict
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from agir.api.redis import using_redislite
from agir.authentication.crypto import connection_token_generator, short_code_generator
from agir.events.models import Event
from agir.groups.models import SupportGroup
from agir.people.models import Person


@using_redislite
class MailLinkTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_person("test@test.com")
        self.person2 = Person.objects.create_person("test2@test.com")

        self.soft_backend = "agir.authentication.backend.MailLinkBackend"

    def test_can_connect_with_query_params(self):
        p = self.person.pk
        code = connection_token_generator.make_token(user=self.person)

        response = self.client.get(reverse("volunteer"), data={"p": p, "code": code})

        self.assertRedirects(response, reverse("volunteer"))
        self.assertEqual(get_user(self.client), self.person.role)

    def test_cannot_connect_with_query_params_if_salt_changed(self):
        p = self.person.pk
        code = connection_token_generator.make_token(user=self.person)
        self.person.auto_login_salt = "something"
        self.person.save()

        response = self.client.get(
            reverse("volunteer"), data={"p": p, "code": code}, follow=True
        )

        self.assertIn(
            (reverse("short_code_login") + "?next=" + reverse("volunteer"), 302),
            response.redirect_chain,
        )

    def test_cannot_connect_with_wrong_query_params(self):
        p = self.person.pk

        response = self.client.get(
            reverse("volunteer"), data={"p": p, "code": "prout"}, follow=True
        )

        self.assertIn(
            (reverse("short_code_login") + "?next=" + reverse("volunteer"), 302),
            response.redirect_chain,
        )

    def test_can_access_soft_login_while_already_connected(self):
        self.client.force_login(self.person.role, self.soft_backend)

        response = self.client.get(reverse("volunteer"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @mock.patch("agir.authentication.forms.send_login_email")
    def test_short_code_page_when_access_hard_loggin_page_while_soft_logged_in(
        self, send_login_email
    ):
        self.client.force_login(self.person.role, self.soft_backend)

        response = self.client.get(reverse("create_group"), follow=True)
        self.assertContains(
            response,
            f"Pour vous authentifier, un e-mail vous a été envoyé à {self.person.email}",
        )
        self.assertRedirects(
            response,
            reverse("check_short_code", args=[self.person.pk])
            + "?next="
            + reverse("create_group"),
        )
        send_login_email.apply_async.assert_called_once()

    def test_unsubscribe_shows_direct_unsubscribe_form_when_logged_in(self):
        message_preferences_path = reverse("contact")
        unsubscribe_path = reverse("unsubscribe")

        self.client.force_login(self.person.role)
        response = self.client.get(unsubscribe_path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, self.person.email)
        self.assertContains(response, 'action="{}"'.format(message_preferences_path))


@using_redislite
class ShortCodeTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_person("test@test.com")

    def test_using_send_mail_form(self):
        send_mail_link = reverse("short_code_login")

        res = self.client.get(send_mail_link)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res = self.client.post(send_mail_link, {"email": "test@test.com"})
        self.assertRedirects(
            res, reverse("check_short_code", kwargs={"user_pk": self.person.pk})
        )

    def test_checking_code(self):
        check_short_code_link = reverse(
            "check_short_code", kwargs={"user_pk": self.person.pk}
        )
        code, expiry = short_code_generator.generate_short_code(self.person.pk)

        res = self.client.get(check_short_code_link)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res = self.client.post(check_short_code_link, {"code": code})
        self.assertRedirects(res, "/")

    def test_warned_if_using_wrong_format(self):
        check_short_code_link = reverse(
            "check_short_code", kwargs={"user_pk": self.person.pk}
        )
        res = self.client.post(check_short_code_link, {"code": "mù**2,;"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.context_data["form"].has_error("code", "incorrect_format"))

    def test_cannot_send_mail_with_invalid_email(self):
        send_mail_link = reverse("short_code_login")

        res = self.client.post(send_mail_link, {"email": "testtest.com"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.context_data["form"].has_error("email", "invalid"))

    def test_cannot_send_mail_with_unknown(self):
        send_mail_link = reverse("short_code_login")

        res = self.client.post(send_mail_link, {"email": "unknown@test.com"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.context_data["form"].has_error("email", "unknown"))

    def test_known_mails_feature(self):
        res = self.client.post(reverse("short_code_login"), {"email": "test@test.com"})
        self.assertRedirects(
            res, reverse("check_short_code", kwargs={"user_pk": self.person.pk})
        )

        self.assertEqual(res.cookies["knownEmails"].value, "test@test.com")

    @mock.patch("agir.lib.token_bucket.get_current_timestamp")
    def test_send_mail_rate_limiting(self, current_timestamp_mock):
        send_mail_link = reverse("short_code_login")
        send_mail = lambda: self.client.post(send_mail_link, {"email": "test@test.com"})

        # we should be limited when sending 10 mails in a go
        for i in range(10):
            current_timestamp_mock.return_value = i
            res = send_mail()

            if res.status_code == status.HTTP_200_OK and res.context_data[
                "form"
            ].has_error("email", "rate_limited"):
                break
        else:
            self.fail("Not rate limited")

        # we should be able to send another mail 30 minutes later
        current_timestamp_mock.return_value = 30 * 60
        res = send_mail()
        self.assertRedirects(
            res, reverse("check_short_code", kwargs={"user_pk": self.person.pk})
        )

    def test_cannot_check_code_with_unknown_person(self):
        check_code_link = reverse("check_short_code", kwargs={"user_pk": uuid.uuid4()})
        self.assertRedirects(
            self.client.post(check_code_link), reverse("short_code_login")
        )

    @mock.patch("agir.lib.token_bucket.get_current_timestamp")
    def test_check_code_rate_limiting(self, current_timestamp_mock):
        check_code_link = reverse(
            "check_short_code", kwargs={"user_pk": self.person.pk}
        )
        wrong_code = short_code_generator._make_code()
        try_code = lambda: self.client.post(check_code_link, {"code": wrong_code})

        # should be rate limited when trying 10 times
        for i in range(10):
            current_timestamp_mock.return_value = i
            res = try_code()

            if res.status_code == status.HTTP_200_OK and res.context_data[
                "form"
            ].has_error("code", "rate_limited"):
                break
        else:
            self.fail("Not rate limited")

        # should be able to try again half an hour later
        current_timestamp_mock.return_value = 30 * 60
        res = try_code()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.context_data["form"].has_error("code", "wrong_code"))

    def test_get_debounced_when_connecting(self):
        primary_email = self.person.primary_email
        primary_email.bounced = True
        primary_email.save()

        self.person.add_email("another_address@example.com", _bounced=True)

        check_short_code_url = reverse(
            "check_short_code", kwargs={"user_pk": self.person.pk}
        )

        res = self.client.post(
            reverse("short_code_login"), data={"email": "another_address@example.com"}
        )
        self.assertRedirects(res, check_short_code_url)

        code_email = mail.outbox[0]
        code = re.search(
            r"^ {4}([A-Z0-9]{3} [A-Z0-9]{2})", code_email.body, re.MULTILINE
        ).group(1)

        res = self.client.post(check_short_code_url, data={"code": code})
        self.assertRedirects(res, "/")

        new_primary_email = self.person.emails.first()
        self.assertEqual(new_primary_email.address, "another_address@example.com")
        self.assertFalse(new_primary_email.bounced)


class AuthorizationTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_person("test@test.com")

        now = timezone.now()
        day = timezone.timedelta(days=1)
        hour = timezone.timedelta(hours=1)

        self.event = Event.objects.create(
            name="event", start_time=now + day, end_time=now + day + hour
        )

        self.group = SupportGroup.objects.create(name="group")

    def test_redirect_when_unauth(self):
        for url in [
            "/",
            "/evenements/creer/",
            "/groupes/creer/",
            reverse("edit_event", args=[self.group.pk]),
            reverse("edit_group", args=[self.group.pk]),
        ]:
            response = self.client.get(url)
            query = QueryDict(mutable=True)
            query["next"] = url
            self.assertRedirects(response, "/connexion/?%s" % query.urlencode(safe="/"))

    def test_403_when_editing_event(self):
        self.client.force_login(self.person.role)

        response = self.client.get("/evenements/%s/modifier/" % self.event.pk)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.post("/evenements/%s/modifier/" % self.event.pk)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_403_when_editing_group(self):
        self.client.force_login(self.person.role)

        response = self.client.get(reverse("edit_group", args=[self.group.pk]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.post(reverse("edit_group", args=[self.group.pk]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_deconnexion_link_when_hard_login_in(self):
        self.client.force_login(self.person.role)

        response = self.client.get(reverse("short_code_login"))
        self.assertContains(
            response, "Vous êtes déjà connecté", count=1, status_code=200, msg_prefix=""
        )
