import base64
import uuid

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.utils import timezone
from oauth2_provider.models import AccessToken
from rest_framework import exceptions, status
from rest_framework.test import APIRequestFactory, APITestCase

from agir.clients.authentication import AccessTokenAuthentication
from . import models, authentication, scopes
from ..authentication.models import Role
from ..people.models import Person


class TokenTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_insoumise(
            email="test@test.com", create_role=True
        )
        self.scope = scopes.view_profile
        self.other_scope = scopes.edit_profile
        self.client = models.Client.objects.create_client(
            "client", scopes=[self.scope.name, self.other_scope.name]
        )
        self.one_scope_client = models.Client.objects.create_client(
            "noscope", scopes=[self.other_scope.name]
        )

        self.token = AccessToken.objects.create(
            user=self.person.role,
            token=str(uuid.uuid4()),
            scope=" ".join([self.scope.name, self.other_scope.name]),
            application=self.client,
            expires=timezone.now() + timezone.timedelta(days=1),
        )

        self.wrong_scope_token = AccessToken.objects.create(
            user=self.person.role,
            token=str(uuid.uuid4()),
            scope=" ".join([self.scope.name, self.other_scope.name]),
            application=self.one_scope_client,
            expires=timezone.now() + timezone.timedelta(days=1),
        )

        self.factory = APIRequestFactory()
        self.token_authentifier = AccessTokenAuthentication()

    def test_cannot_authenticate_with_invalid_token(self):
        request = self.factory.get(
            "", HTTP_AUTHORIZATION="Bearer {token}".format(token=str(uuid.uuid4()))
        )

        self.assertIsNone(self.token_authentifier.authenticate(request=request))

    def test_can_authenticate_with_token(self):
        request = self.factory.get(
            "", HTTP_AUTHORIZATION="Bearer {token}".format(token=self.token)
        )

        auth_user, auth_info = self.token_authentifier.authenticate(request=request)

        self.assertEqual(auth_user.type, Role.PERSON_ROLE)
        self.assertEqual(auth_user.person, self.person)
        self.assertEqual(auth_user.token, auth_info)
        self.assertIsInstance(auth_info, AccessToken)
        self.assertEqual(auth_info.application, self.client)
        self.assertCountEqual(
            auth_info.scopes, [self.scope.name, self.other_scope.name]
        )


class ScopeTestCase(APITestCase):
    def setUp(self):
        # We create a superuser and a client with all scopes
        # Then we create token with smaller scopes to test
        person_content_type = ContentType.objects.get_for_model(Person)
        self.person = Person.objects.create_superperson(
            email="test@test.com", password="randomstring", create_role=True
        )
        add_permission = Permission.objects.get(
            content_type=person_content_type, codename="view_person"
        )
        self.person.role.user_permissions.add(add_permission)
        self.other_person = Person.objects.create_insoumise(email="test2@test.com")

        self.api_client = models.Client.objects.create_client(
            "client", scopes=scopes.scopes_names
        )

    def generate_token(self, scopes_names):
        self.token = AccessToken.objects.create(
            user=self.person.role,
            token=str(uuid.uuid4()),
            scope=" ".join(scopes_names),
            application=self.api_client,
            expires=timezone.now() + timezone.timedelta(days=1),
        )
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer {token}".format(token=self.token)
        )

    def test_get_required_token(self):
        self.assertEqual(
            scopes.get_required_scopes("people.view_person"), [scopes.view_profile]
        )


class ClientTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.client = models.Client.objects.create_client("client", "password")
        self.superclient = models.Client.objects.create_superclient(
            "superclient", "password"
        )

        self.client_authentifier = authentication.ClientAuthentication()

    def get_auth_header(self, label, password):
        return b"Basic " + base64.b64encode(
            "{label}:{password}".format(label=label, password=password).encode("ascii")
        )

    def test_cannot_authenticate_with_wrong_password(self):
        request = self.factory.get(
            "", HTTP_AUTHORIZATION=self.get_auth_header("client", "zef")
        )

        with self.assertRaises(exceptions.AuthenticationFailed):
            self.client_authentifier.authenticate(request=request)

    def test_can_authenticate_client(self):
        request = self.factory.get(
            "", HTTP_AUTHORIZATION=self.get_auth_header("client", "password")
        )

        authentified_user, auth_info = self.client_authentifier.authenticate(
            request=request
        )

        self.assertEqual(authentified_user.type, Role.CLIENT_ROLE)
        self.assertEqual(authentified_user.client, self.client)
        self.assertIsNone(auth_info)

    def test_can_check_superclient_permissions(self):
        request = self.factory.get(
            "", HTTP_AUTHORIZATION=self.get_auth_header("superclient", "password")
        )

        authentified_user, auth_info = self.client_authentifier.authenticate(
            request=request
        )

        self.assertEqual(authentified_user.type, Role.CLIENT_ROLE)
        self.assertEqual(authentified_user.client, self.superclient)
        self.assertIsNone(auth_info)

        assert authentified_user.has_perm("people.view_person")
        assert authentified_user.has_perm("events.change_event")


class ScopeViewSetTestCase(APITestCase):
    """Test the Scope endpoint"""

    def test_can_see_scopes_while_unauthenticated(self):
        response = self.client.get("/legacy/scopes/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(
            [s["name"] for s in response.data],
            [
                "view_profile",
                "edit_profile",
                "edit_event",
                "edit_rsvp",
                "edit_supportgroup",
                "view_membership",
                "edit_membership",
                "edit_authorization",
                "toktok",
            ],
        )

    def test_can_see_specific_scope_by_label(self):
        response = self.client.get("/legacy/scopes/view_profile/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "view_profile")
        self.assertEqual(response.data["description"], "Voir votre profil")
