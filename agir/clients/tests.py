import base64
import uuid

from oauth2_provider.admin import AccessToken

from django.test import TestCase
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from rest_framework.test import APIRequestFactory, APITestCase
from rest_framework import exceptions, status

from agir.clients.authentication import AccessTokenAuthentication
from . import models, authentication, scopes

from ..people.models import Person
from ..events.models import Event, Calendar, OrganizerConfig, CalendarItem
from ..authentication.models import Role


class TokenTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_person(email="test@test.com")
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
            email="test@test.com", password="randomstring"
        )
        add_permission = Permission.objects.get(
            content_type=person_content_type, codename="view_person"
        )
        self.person.role.user_permissions.add(add_permission)
        self.other_person = Person.objects.create(email="test2@test.com")

        self.calendar = Calendar.objects.create_calendar("calendar")
        self.event = Event.objects.create(
            name="Test event",
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(hours=4),
        )

        CalendarItem.objects.create(event=self.event, calendar=self.calendar)

        OrganizerConfig.objects.create(event=self.event, person=self.person)

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

    def test_can_view_profile_with_correct_scope(self):
        self.generate_token([scopes.view_profile.name])
        response = self.client.get("/legacy/people/me/")
        self.assertEqual(response.status_code, 200)

    def test_cannot_view_profile_without_correct_scope(self):
        self.generate_token([scopes.edit_event.name])
        response = self.client.get("/legacy/people/me/")
        self.assertEqual(response.status_code, 403)

    def test_cannot_use_global_permissions_with_token(self):
        self.generate_token([scopes.view_profile.name])
        response = self.client.get("/legacy/people/" + str(self.other_person.id) + "/")
        self.assertEqual(response.status_code, 403)

    def test_can_edit_profile_with_correct_scope(self):
        self.generate_token([scopes.edit_profile.name])
        response = self.client.patch(
            "/legacy/people/" + str(self.person.id) + "/",
            data={"email": "testedit@test.com"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.person.email, "testedit@test.com")

    def test_cannot_edit_profile_without_correct_scope(self):
        self.generate_token([scopes.view_profile.name])
        response = self.client.patch(
            "/legacy/people/" + str(self.person.id) + "/",
            data={"email": "testedit@test.com"},
        )
        self.assertEqual(response.status_code, 403)

    def test_can_edit_own_event_with_correct_scope(self):
        self.generate_token([scopes.edit_event.name])
        response = self.client.patch(
            "/legacy/events/" + str(self.event.id) + "/",
            data={"description": "Description !"},
        )
        self.event.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.event.description, "Description !")

    def test_cannot_edit_own_event_without_correct_scope(self):
        self.generate_token([scopes.view_profile.name])
        response = self.client.patch(
            "/legacy/events/" + str(self.event.id) + "/",
            data={"description": "Description !"},
        )
        self.event.refresh_from_db()
        self.assertEqual(response.status_code, 403)


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
                "edit_membership",
                "edit_authorization",
            ],
        )

    def test_can_see_specific_scope_by_label(self):
        response = self.client.get("/legacy/scopes/view_profile/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "view_profile")
        self.assertEqual(response.data["description"], "Voir votre profil")
