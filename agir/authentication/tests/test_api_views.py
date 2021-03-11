from rest_framework.test import APITestCase
from unittest.mock import patch

from agir.people.models import Person


class LoginAPITestCase(APITestCase):
    def setUp(self):
        self.valid_email = "valid@email.com"
        self.person = Person.objects.create(
            email=self.valid_email, create_role=True, is_insoumise=True, is_2022=True,
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
