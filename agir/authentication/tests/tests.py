from django.contrib.auth import get_user
from django.http import QueryDict
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from agir.api.redis import using_separate_redis_server
from agir.authentication.tokens import connection_token_generator
from agir.events.models import Event
from agir.groups.models import SupportGroup
from agir.people.models import Person


@using_separate_redis_server
class MailLinkTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_insoumise("test@test.com", create_role=True)
        self.person2 = Person.objects.create_insoumise("test2@test.com")

        self.soft_backend = "agir.authentication.backend.MailLinkBackend"

    def test_can_connect_with_query_params(self):
        p = self.person.pk
        code = connection_token_generator.make_token(user=self.person)

        response = self.client.get(reverse("volunteer"), data={"p": p, "code": code})

        self.assertRedirects(response, reverse("volunteer"))
        self.assertEqual(get_user(self.client), self.person.role)

    def test_can_connect_with_alternative_query_params(self):
        p = self.person.pk
        code = connection_token_generator.make_token(user=self.person)

        response = self.client.get(reverse("volunteer"), data={"_p": p, "code": code})

        self.assertRedirects(response, reverse("volunteer"))
        self.assertEqual(get_user(self.client), self.person.role)

    def test_can_connect_with_query_params_and_app_param(self):
        p = self.person.pk
        code = connection_token_generator.make_token(user=self.person)

        response = self.client.get(
            reverse("volunteer"), data={"p": p, "code": code, "android": 1}
        )

        self.assertRedirects(response, reverse("volunteer") + "?android=1")
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

    def test_short_code_page_when_access_hard_loggin_page_while_soft_logged_in(self):
        self.client.force_login(self.person.role, self.soft_backend)

        response = self.client.get(reverse("create_group"), follow=True)

        self.assertRedirects(
            response,
            reverse("short_code_login") + "?next=" + reverse("create_group"),
        )

    def test_unsubscribe_use_hidden_email_field_when_logged_in(self):
        unsubscribe_path = reverse("unsubscribe")
        self.client.force_login(self.person.role)
        response = self.client.get(unsubscribe_path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, self.person.email)
        self.assertContains(
            response,
            '<input type="hidden" name="email" value="{}" />'.format(self.person.email),
        )


class AuthorizationTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_insoumise("test@test.com", create_role=True)

        now = timezone.now()
        day = timezone.timedelta(days=1)
        hour = timezone.timedelta(hours=1)

        self.event = Event.objects.create(
            name="event", start_time=now + day, end_time=now + day + hour
        )

        self.group = SupportGroup.objects.create(name="group")

    def test_redirect_when_unauth(self):
        for url in [
            "/evenements/creer/",
            "/groupes/creer/",
            reverse("view_event_settings", args=[self.group.pk]),
        ]:
            response = self.client.get(url)
            query = QueryDict(mutable=True)
            query["next"] = url
            self.assertRedirects(response, "/connexion/?%s" % query.urlencode(safe="/"))
