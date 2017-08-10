import base64
import json
import uuid
from redislite import StrictRedis
from unittest import mock, skip

from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from rest_framework.test import APIRequestFactory, force_authenticate, APITestCase
from rest_framework import exceptions, status

from . import models, authentication, tokens
from .viewsets import LegacyClientViewSet

from people.models import Person
from authentication.models import Role


class TokenTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_person(email='test@test.com')
        self.scope = models.Scope.objects.create(label='scope_test')
        self.other_scope = models.Scope.objects.create(label='other_scope')
        self.client = models.Client.objects.create_client('client', scopes=[self.scope, self.other_scope])
        self.one_scope_client = models.Client.objects.create_client('noscope', scopes=[self.other_scope])

        self.redis_instance = StrictRedis()

        self.token = str(uuid.uuid4())
        self.token_info = {
            'clientId':self.client.label,
            'userId': str(self.person.pk),
            'scope': ['scope_test', 'other_scope']
        }

        self.wrong_scope_token = str(uuid.uuid4())
        self.wrong_scope_token_info = {
            'clientId': self.one_scope_client.label,
            'userId': str(self.person.pk),
            'scope': ['scope_test', 'other_scope']
        }

        self.redis_instance.set(
            '{prefix}{token}:payload'.format(prefix=settings.AUTH_REDIS_PREFIX, token=self.token),
            json.dumps(self.token_info)
        )

        self.redis_instance.set(
            '{prefix}{token}:payload'.format(prefix=settings.AUTH_REDIS_PREFIX, token=self.wrong_scope_token),
            json.dumps(self.wrong_scope_token_info)
        )

        self.redis_patcher = mock.patch('clients.tokens.get_auth_redis_client')
        mock_get_auth_redis_client = self.redis_patcher.start()
        mock_get_auth_redis_client.return_value = self.redis_instance

        self.factory = APIRequestFactory()
        self.token_authentifier = authentication.AccessTokenAuthentication()

    def tearDown(self):
        self.redis_patcher.stop()

    def test_cannot_authenticate_with_invalid_token(self):
        request = self.factory.get(
            '',
            HTTP_AUTHORIZATION="Bearer {token}".format(token=str(uuid.uuid4()))
        )

        with self.assertRaises(exceptions.AuthenticationFailed):
            self.token_authentifier.authenticate(request=request)

    def test_can_authenticate_with_token(self):
        request = self.factory.get(
            '',
            HTTP_AUTHORIZATION="Bearer {token}".format(token=self.token)
        )

        auth_user, auth_info = self.token_authentifier.authenticate(request=request)

        self.assertEqual(auth_user.type, Role.PERSON_ROLE)
        self.assertEqual(auth_user.person, self.person)
        self.assertIsInstance(auth_info, tokens.AccessToken)
        self.assertEqual(auth_info.client, self.client)
        self.assertCountEqual(auth_info.scopes, [self.scope, self.other_scope])

    def test_only_scopes_authorized_for_client_are_kept(self):
        request = self.factory.get(
            '',
            HTTP_AUTHORIZATION="Bearer {token}".format(token=self.wrong_scope_token)
        )

        auth_user, auth_info = self.token_authentifier.authenticate(request=request)

        self.assertEqual(auth_info.client, self.one_scope_client)
        self.assertCountEqual(auth_info.scopes, [self.other_scope])


class ClientTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.client = models.Client.objects.create_client('client', 'password')
        self.superclient = models.Client.objects.create_superclient('superclient', 'password')

        self.client_authentifier = authentication.ClientAuthentication()

    def get_auth_header(self, label, password):
        return b"Basic " + base64.b64encode("{label}:{password}".format(label=label, password=password).encode('ascii'))

    def test_cannot_authenticate_with_wrong_password(self):
        request = self.factory.get(
            '',
            HTTP_AUTHORIZATION=self.get_auth_header('client', 'zef')
        )

        with self.assertRaises(exceptions.AuthenticationFailed):
            self.client_authentifier.authenticate(request=request)

    def test_can_authenticate_client(self):
        request = self.factory.get(
            '',
            HTTP_AUTHORIZATION=self.get_auth_header('client', 'password')
        )

        authentified_user, auth_info = self.client_authentifier.authenticate(request=request)

        self.assertEqual(authentified_user.type, Role.CLIENT_ROLE)
        self.assertEqual(authentified_user.client, self.client)
        self.assertIsNone(auth_info)

    def test_can_check_superclient_permissions(self):
        request = self.factory.get(
            '',
            HTTP_AUTHORIZATION=self.get_auth_header('superclient', 'password')
        )

        authentified_user, auth_info = self.client_authentifier.authenticate(request=request)

        self.assertEqual(authentified_user.type, Role.CLIENT_ROLE)
        self.assertEqual(authentified_user.client, self.superclient)
        self.assertIsNone(auth_info)

        assert authentified_user.has_perm('people.view_person')
        assert authentified_user.has_perm('events.change_event')


class LegacyClientViewSetTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.client_unprivileged = models.Client.objects.create_client('unprivileged', 'password')
        self.viewer_client = models.Client.objects.create_client('viewer', 'password')

        client_content_type = ContentType.objects.get_for_model(models.Client)
        view_permission = Permission.objects.get(content_type=client_content_type, codename='view_client')

        self.viewer_client.role.user_permissions.add(view_permission)

        self.detail_view = LegacyClientViewSet.as_view({
            'get': 'retrieve',
            'put': 'update',
            'patch': 'partial_update',
            'delete': 'destroy'
        })

        self.list_view = LegacyClientViewSet.as_view({
            'get': 'list',
            'post': 'create'
        })

        self.authenticate_view = LegacyClientViewSet.as_view({
            'post': 'authenticate_client'
        })

    def test_cannot_see_while_unauthenticated(self):
        request = self.factory.get('')

        response = self.list_view(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.detail_view(request, pk=self.client_unprivileged.pk)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_can_only_see_self_if_unprivileged(self):
        request = self.factory.get('')
        force_authenticate(request, self.client_unprivileged.role)
        response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['_items']), 1)
        self.assertEqual(response.data['_items'][0]['id'], self.client_unprivileged.label)

    def test_can_list_clients(self):
        request = self.factory.get('')
        force_authenticate(request, self.viewer_client.role)
        response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AuthenticateClientViewTestCase(APITestCase):
    """Test the authenticate_view route of the :py:class:`clients.viewsets.LegacyClientViewSet`

    Additional routes with specific permission classes must be tested through the APIClient as the
    permission classes won't be replaced by
    """
    def setUp(self):
        self.client_unprivileged = models.Client.objects.create_client('unprivileged', 'password')
        self.client_oauth = models.Client.objects.create_client('oauth', 'password', oauth_enabled=True)
        self.viewer_client = models.Client.objects.create_client('viewer', 'password')

        client_content_type = ContentType.objects.get_for_model(models.Client)
        view_permission = Permission.objects.get(content_type=client_content_type, codename='view_client')

        self.viewer_client.role.user_permissions.add(view_permission)

    def test_cannot_verify_client_if_unauthenticated(self):
        response = self.client.post('/legacy/clients/authenticate_client/', data={'id': 'test', 'secret': 'test'})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_verify_client_if_no_view_permission(self):
        self.client.force_authenticate(user=self.client_unprivileged.role)
        response = self.client.post('/legacy/clients/authenticate_client/', data={'id': 'test', 'secret': 'test'})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_verify_non_oauth_client(self):
        self.client.force_authenticate(user=self.viewer_client.role)
        response = self.client.post('/legacy/clients/authenticate_client/', data={'id': 'unprivileged', 'secret': 'password'})

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_can_verify_client_with_view_permission(self):
        self.client.force_authenticate(user=self.viewer_client.role)
        response = self.client.post('/legacy/clients/authenticate_client/', data={'id': 'oauth', 'secret': 'password'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['_id'], str(self.client_oauth.id))

    def test_unprocessable_entity_if_wrong_client_id(self):
        self.client.force_authenticate(user=self.viewer_client.role)
        response = self.client.post('/legacy/clients/authenticate_client/', data={'id': 'wrong', 'secret': 'wrong'})

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_unprocessable_entity_if_wrong_client_secret(self):
        self.client.force_authenticate(user=self.viewer_client.role)
        response = self.client.post('/legacy/clients/authenticate_client/', data={'id': 'unprivileged', 'secret': 'wrong'})

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)


class ScopeViewSetTestCase(APITestCase):
    """Test the Scope endpoint"""

    def setUp(self):
        self.scope1 = models.Scope.objects.create(label='scope1', description='Un super scope de ouf')
        self.scope2 = models.Scope.objects.create(label='scope2', description='Un autre scope de ouf')

    def test_can_see_scopes_while_unauthenticated(self):
        response = self.client.get('/legacy/scopes/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual([s['label'] for s in response.data], [s.label for s in models.Scope.objects.all()])

    @skip("TODO")
    def test_can_see_specific_scope(self):
        pass

    @skip("TODO")
    def test_cannot_modify_while_unprivileged(self):
        pass

    @skip("TODO")
    def test_can_modify(self):
        pass

    @skip("TODO")
    def test_cannot_delete(self):
        pass


class AuthorizationViewSetTestCase(APITestCase):
    """Test the authorization endpoint
    """

    def setUp(self):
        pass

    @skip("TODO")
    def test_cannot_see_authorization_while_unauthenticate(self):
        pass

    @skip("TODO")
    def test_can_only_see_own_when_unprivileged(self):
        pass

    @skip("TODO")
    def test_can_see_all_with_privileges(self):
        pass

    @skip("TODO")
    def test_can_modify_own_when_unprivileged(self):
        pass

    @skip("TODO")
    def test_cannot_modify_other_than_own_when_unprivileged(self):
        pass

    @skip("TODO")
    def test_can_delete_own(self):
        pass

    @skip("TODO")
    def test_cannot_delete_other_than_own(self):
        pass
