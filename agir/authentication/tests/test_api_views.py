from unittest.mock import patch

from rest_framework.test import APITestCase

from agir.authentication.tokens import short_code_generator
from agir.people.models import Person


class LoginAPITestCase(APITestCase):
    def setUp(self):
        self.valid_email = "valid@email.com"
        self.person = Person.objects.create_person(
            email=self.valid_email, create_role=True, is_political_support=True
        )

    def test_person_cannot_login_with_empty_email(self):
        self.client.logout()
        email = ""
        res = self.client.post(f"/api/connexion/", data={"email": email})
        self.assertEqual(res.status_code, 422)
        self.assertIn("email", res.data)

    def test_person_cannot_login_with_invalid_email(self):
        self.client.logout()
        email = "invalid email"
        res = self.client.post(f"/api/connexion/", data={"email": email})
        self.assertEqual(res.status_code, 422)
        self.assertIn("email", res.data)

    @patch(
        "agir.authentication.views.api_views.send_mail_email_bucket.has_tokens",
        return_value=False,
    )
    def test_person_cannot_login_if_email_is_throttled(self, email_bucket):
        self.client.logout()
        email = self.valid_email
        res = self.client.post(f"/api/connexion/", data={"email": email})
        self.assertEqual(res.status_code, 429)
        self.assertIn("detail", res.data)

    @patch(
        "agir.authentication.views.api_views.send_mail_email_bucket.has_tokens",
        return_value=True,
    )
    @patch(
        "agir.authentication.views.api_views.send_mail_ip_bucket.has_tokens",
        return_value=False,
    )
    def test_person_cannot_login_if_ip_address_is_throttled(
        self, email_bucket, ip_bucket
    ):
        self.client.logout()
        email = self.valid_email
        res = self.client.post(f"/api/connexion/", data={"email": email})
        self.assertEqual(res.status_code, 429)
        self.assertIn("detail", res.data)

    @patch(
        "agir.authentication.views.api_views.send_mail_email_bucket.has_tokens",
        return_value=True,
    )
    @patch(
        "agir.authentication.views.api_views.send_mail_ip_bucket.has_tokens",
        return_value=True,
    )
    def test_person_can_login_if_email_is_valid_and_email_and_ip_address_are_not_throttled(
        self, email_bucket, ip_bucket
    ):
        self.client.logout()
        email = self.valid_email
        res = self.client.post(f"/api/connexion/", data={"email": email})
        self.assertEqual(res.status_code, 200)

    @patch("agir.authentication.views.api_views.send_login_email.apply_async")
    def test_user_will_be_send_a_login_email_if_already_registered(
        self, send_login_email
    ):
        send_login_email.assert_not_called()
        self.client.logout()
        email = self.person.email
        res = self.client.post(f"/api/connexion/", data={"email": email})
        self.assertEqual(res.status_code, 200)
        send_login_email.assert_called()

    @patch("agir.authentication.views.api_views.send_no_account_email.delay")
    def test_user_will_be_send_a_no_account_email_if_not_registered(
        self, send_no_account_email
    ):
        send_no_account_email.assert_not_called()
        self.client.logout()
        email = "unknown@email.com"
        res = self.client.post(f"/api/connexion/", data={"email": email})
        self.assertEqual(res.status_code, 200)
        send_no_account_email.assert_called()


class CheckCodeTestCase(APITestCase):
    def setUp(self):
        self.primary_email = "person@email.com"
        self.person = Person.objects.create_person(
            email=self.primary_email, create_role=True, is_political_support=True
        )

    def test_person_cannot_login_without_a_session_email(self):
        session = self.client.session
        session["login_email"] = None
        session.save()
        code, expiry = short_code_generator.generate_short_code(self.person.email)
        res = self.client.post(f"/api/connexion/code/", data={"code": code})
        self.assertEqual(res.status_code, 405)

    def test_person_cannot_login_without_sending_a_code(self):
        session = self.client.session
        session["login_email"] = self.person.email
        session.save()
        code = ""
        res = self.client.post(f"/api/connexion/code/", data={"code": code})
        self.assertEqual(res.status_code, 422)
        self.assertIn("code", res.data)

    @patch(
        "agir.authentication.views.api_views.short_code_generator.is_allowed_pattern",
        return_value=False,
    )
    def test_person_cannot_login_with_a_bad_formatted_code(self, is_allowed_pattern):
        session = self.client.session
        session["login_email"] = self.person.email
        session.save()
        code = "Not a valid code !!!"
        res = self.client.post(f"/api/connexion/code/", data={"code": code})
        self.assertEqual(res.status_code, 422)
        self.assertIn("code", res.data)

    @patch(
        "agir.authentication.views.api_views.check_short_code_bucket.has_tokens",
        return_value=False,
    )
    def test_person_cannot_login_if_short_code_is_throttled(self, short_code_bucket):
        session = self.client.session
        session["login_email"] = self.person.email
        session.save()
        code, expiry = short_code_generator.generate_short_code(self.person.email)
        res = self.client.post(f"/api/connexion/code/", data={"code": code})
        self.assertEqual(res.status_code, 429)
        self.assertIn("detail", res.data)

    @patch(
        "agir.authentication.views.api_views.check_short_code_bucket.has_tokens",
        return_value=True,
    )
    @patch(
        "agir.authentication.views.api_views.authenticate",
        return_value=False,
    )
    def test_person_cannot_login_if_short_code_is_not_valid(
        self, short_code_bucket, authenticate
    ):
        session = self.client.session
        session["login_email"] = self.person.email
        session.save()
        code, expiry = short_code_generator.generate_short_code(self.person.email)
        res = self.client.post(f"/api/connexion/code/", data={"code": code})
        self.assertEqual(res.status_code, 422)
        self.assertIn("code", res.data)

    def test_person_can_login_if_short_code_is_valid(self):
        session_res = self.client.get("/api/session/")
        self.assertIn("user", session_res.data)
        self.assertEqual(session_res.data["user"], False)

        session = self.client.session
        session["login_email"] = self.person.email
        session.save()
        code, expiry = short_code_generator.generate_short_code(self.person.email)
        res = self.client.post(f"/api/connexion/code/", data={"code": code})
        self.assertEqual(res.status_code, 200)
        self.assertIn("lastLogin", res.data)

        session_res = self.client.get("/api/session/")
        self.assertIn("user", session_res.data)
        self.assertIn("email", session_res.data["user"])
        self.assertEqual(session_res.data["user"]["email"], self.person.email)

    def test_email_is_debounced_if_login_succeeds(self):
        email = self.person.emails.get_by_natural_key(self.person.email)
        email.bounced = True
        email.save()
        session = self.client.session
        session["login_email"] = self.person.email
        session.save()
        code, expiry = short_code_generator.generate_short_code(self.person.email)
        res = self.client.post(f"/api/connexion/code/", data={"code": code})
        self.assertEqual(res.status_code, 200)
        email = self.person.emails.get_by_natural_key(self.person.email)
        self.assertFalse(email.bounced)


class LogoutTestCase(APITestCase):
    def setUp(self):
        self.primary_email = "person@email.com"
        self.person = Person.objects.create_person(
            email=self.primary_email, create_role=True, is_political_support=True
        )

    def test_person_can_logout(self):
        self.client.force_login(self.person.role)
        session_res = self.client.get("/api/session/")
        self.assertIn("user", session_res.data)
        self.assertIn("email", session_res.data["user"])
        self.assertEqual(session_res.data["user"]["email"], self.person.email)

        res = self.client.get(f"/api/deconnexion/")
        self.assertEqual(res.status_code, 200)

        session_res = self.client.get("/api/session/")
        self.assertIn("user", session_res.data)
        self.assertEqual(session_res.data["user"], False)
