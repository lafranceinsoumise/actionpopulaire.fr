from unittest import TestCase
from unittest.mock import MagicMock

from oauth2_provider.contrib.rest_framework import (
    OAuth2Authentication,
)

from agir.lib.rest_framework_permissions import (
    IsActionPopulaireClientPermission,
    IsPersonPermission,
    IsPersonOrTokenHasScopePermission,
)


class IsActionPopulairePermissionTestCase(TestCase):
    def setUp(self):
        self.permission = IsActionPopulaireClientPermission()
        self.request = MagicMock(user=MagicMock(), successful_authenticator=None)
        self.view = MagicMock()

    def test_permission_is_denied_for_oauth2_authenticated_requests(self):
        self.request.successful_authenticator = OAuth2Authentication()
        self.assertFalse(self.permission.has_permission(self.request, self.view))

    def test_permission_is_granted_for_non_oauth2_authenticated_requests(self):
        self.request.successful_authenticator = None
        self.assertTrue(self.permission.has_permission(self.request, self.view))


class IsPersonPermissionTestCase(TestCase):
    def setUp(self):
        self.permission = IsPersonPermission()
        self.request = MagicMock(
            user=MagicMock(is_authenticated=True, person=MagicMock()),
            successful_authenticator=None,
        )
        self.view = MagicMock()

    def test_permission_is_denied_for_oauth2_authenticated_requests(self):
        self.request.successful_authenticator = OAuth2Authentication()
        self.request.user.is_authenticated = True
        self.request.user.person = MagicMock()
        self.assertFalse(self.permission.has_permission(self.request, self.view))

    def test_permission_is_denied_for_non_authenticated_users(self):
        self.request.successful_authenticator = None
        self.request.user.is_authenticated = False
        self.request.user.person = MagicMock()
        self.assertFalse(self.permission.has_permission(self.request, self.view))

    def test_permission_is_denied_for_authenticated_users_without_a_person(self):
        self.request.successful_authenticator = None
        self.request.user.is_authenticated = True
        self.request.user.person = None
        self.assertFalse(self.permission.has_permission(self.request, self.view))

    def test_permission_is_granted_for_authenticated_users_with_a_person(self):
        self.request.successful_authenticator = None
        self.request.user.is_authenticated = True
        self.request.user.person = MagicMock()
        self.assertTrue(self.permission.has_permission(self.request, self.view))


class IsPersonOrTokenHasScopePermissionTestCase(TestCase):
    def setUp(self):
        self.permission = IsPersonOrTokenHasScopePermission()
        self.view = MagicMock()

    def get_auth(self, required_scopes, token_scopes):
        auth = MagicMock()
        auth.is_valid.return_value = bool(set(required_scopes) & set(token_scopes))
        return auth

    def make_request(
        self,
        is_authenticated=True,
        is_person=True,
        is_oauth2=True,
        required_scopes=(),
        token_scopes=(),
    ):
        return MagicMock(
            user=MagicMock(
                is_authenticated=is_authenticated,
                person=(MagicMock() if is_person else None),
            ),
            successful_authenticator=OAuth2Authentication() if is_oauth2 else None,
            required_scopes=required_scopes,
            auth=self.get_auth(required_scopes, token_scopes),
        )

    def test_permission_is_denied_for_non_authenticated_users(self):
        request = self.make_request(is_authenticated=False)
        self.assertFalse(self.permission.has_permission(request, self.view))

    def test_permission_is_denied_for_authenticated_users_without_a_person(self):
        request = self.make_request(is_authenticated=True, is_person=False)
        self.assertFalse(self.permission.has_permission(request, self.view))

    def test_permission_is_denied_for_oauth2_token_without_the_right_scope(self):
        request = self.make_request(
            is_authenticated=True,
            is_person=True,
            is_oauth2=True,
            required_scopes=["delete"],
            token_scopes=["read"],
        )
        self.assertFalse(self.permission.has_permission(request, self.view))

    def test_permission_is_granted_for_oauth2_token_with_the_right_scope(self):
        request = self.make_request(
            is_authenticated=True,
            is_person=True,
            is_oauth2=True,
            required_scopes=["delete"],
            token_scopes=["read", "delete"],
        )
        self.assertTrue(self.permission.has_permission(request, self.view))

    def test_permission_is_granted_for_non_oauth2_authenticated_requests(self):
        request = self.make_request(
            is_authenticated=True, is_person=True, is_oauth2=False
        )
        self.assertTrue(self.permission.has_permission(request, self.view))
