import base64
import json
import uuid
from urllib.parse import urlparse

from redislite import StrictRedis
from unittest import mock, skip

from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from rest_framework.test import APIRequestFactory, force_authenticate, APITestCase
from rest_framework.reverse import reverse
from rest_framework import exceptions, status

from . import models, authentication, tokens, scopes
from .viewsets import LegacyClientViewSet

from people.models import Person
from events.models import Event, Calendar, OrganizerConfig
from authentication.models import Role


class TokenTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_person(email='test@test.com')
        self.scope = scopes.view_profile
        self.other_scope = scopes.edit_profile
        self.client = models.Client.objects.create_client('client', scopes=[self.scope.name, self.other_scope.name])
        self.one_scope_client = models.Client.objects.create_client('noscope', scopes=[self.other_scope.name])

        self.redis_instance = StrictRedis()

        self.token = str(uuid.uuid4())
        self.token_info = {
            'clientId': self.client.label,
            'userId': str(self.person.pk),
            'scope': [self.scope.name, self.other_scope.name]
        }

        self.wrong_scope_token = str(uuid.uuid4())
        self.wrong_scope_token_info = {
            'clientId': self.one_scope_client.label,
            'userId': str(self.person.pk),
            'scope': [self.scope.name, self.other_scope.name]
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
        self.assertEqual(auth_user.token, auth_info)
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


class ScopeTestCase(APITestCase):
    def setUp(self):
        # We create a superuser and a client with all scopes
        # Then we create token with smaller scopes to test
        person_content_type = ContentType.objects.get_for_model(Person)
        self.person = Person.objects.create_superperson(email='test@test.com', password='randomstring')
        add_permission = Permission.objects.get(content_type=person_content_type, codename='view_person')
        self.person.role.user_permissions.add(add_permission)
        self.other_person = Person.objects.create(email='test2@test.com')

        self.calendar = Calendar.objects.create_calendar('calendar')
        self.event = Event.objects.create(
            name='Test event',
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(hours=4),
            calendar=self.calendar
        )

        OrganizerConfig.objects.create(
            event=self.event,
            person=self.person
        )

        self.api_client = models.Client.objects.create_client('client', scopes=scopes.scopes_names)
        self.redis_instance = StrictRedis()
        self.redis_patcher = mock.patch('clients.tokens.get_auth_redis_client')
        mock_get_auth_redis_client = self.redis_patcher.start()
        mock_get_auth_redis_client.return_value = self.redis_instance

    def tearDown(self):
        self.redis_patcher.stop()

    def generate_token(self, scopes_names):
        self.token = str(uuid.uuid4())
        self.token_info = {
            'clientId': self.api_client.label,
            'userId': str(self.person.pk),
            'scope': scopes_names
        }
        self.redis_instance.set(
            '{prefix}{token}:payload'.format(prefix=settings.AUTH_REDIS_PREFIX, token=self.token),
            json.dumps(self.token_info)
        )
        self.client.credentials(HTTP_AUTHORIZATION="Bearer {token}".format(token=self.token))

    def test_get_required_token(self):
        self.assertEqual(scopes.get_required_scopes('people.view_person'), [scopes.view_profile])

    def test_can_view_profile_with_correct_scope(self):
        self.generate_token([scopes.view_profile.name])
        response = self.client.get('/legacy/people/me/')
        self.assertEqual(response.status_code, 200)

    def test_cannot_view_profile_without_correct_scope(self):
        self.generate_token([scopes.edit_event.name])
        response = self.client.get('/legacy/people/me/')
        self.assertEqual(response.status_code, 403)

    def test_cannot_use_global_permissions_with_token(self):
        self.generate_token([scopes.view_profile.name])
        response = self.client.get('/legacy/people/' + str(self.other_person.id) + '/')
        self.assertEqual(response.status_code, 403)

    def test_can_edit_profile_with_correct_scope(self):
        self.generate_token([scopes.edit_profile.name])
        response = self.client.patch(
            '/legacy/people/' + str(self.person.id) + '/',
            data={'email': 'testedit@test.com'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.person.email, 'testedit@test.com')

    def test_cannot_edit_profile_without_correct_scope(self):
        self.generate_token([scopes.view_profile.name])
        response = self.client.patch(
            '/legacy/people/' + str(self.person.id) + '/',
            data={'email': 'testedit@test.com'}
        )
        self.assertEqual(response.status_code, 403)

    def test_can_edit_own_event_with_correct_scope(self):
        self.generate_token([scopes.edit_event.name])
        response = self.client.patch(
            '/legacy/events/' + str(self.event.id) + '/',
            data={'description': 'Description !'}
        )
        self.event.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.event.description, 'Description !')

    def test_cannot_edit_own_event_without_correct_scope(self):
        self.generate_token([scopes.view_profile.name])
        response = self.client.patch(
            '/legacy/events/' + str(self.event.id) + '/',
            data={'description': 'Description !'}
        )
        self.event.refresh_from_db()
        self.assertEqual(response.status_code, 403)


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
        response = self.client.post('/legacy/clients/authenticate_client/',
                                    data={'id': 'unprivileged', 'secret': 'password'})

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
        response = self.client.post('/legacy/clients/authenticate_client/',
                                    data={'id': 'unprivileged', 'secret': 'wrong'})

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)


class ScopeViewSetTestCase(APITestCase):
    """Test the Scope endpoint"""
    def test_can_see_scopes_while_unauthenticated(self):
        response = self.client.get('/legacy/scopes/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual([s['name'] for s in response.data], [
            'view_profile',
            'edit_profile',
            'edit_event',
            'edit_rsvp',
            'edit_supportgroup',
            'edit_membership',
            'edit_authorization',
        ])

    def test_can_see_specific_scope_by_label(self):
        response = self.client.get('/legacy/scopes/view_profile/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'view_profile')
        self.assertEqual(response.data['description'], 'Voir mon profil')


class AuthorizationViewSetTestCase(APITestCase):
    """Test the authorization endpoint
    """

    def setUp(self):
        self.privileged_client = models.Client.objects.create_client('superclient')
        self.unprivileged_client = models.Client.objects.create_client('client', oauth_enabled=True)

        self.oauth_client = models.Client.objects.create_client('oauth_client', oauth_enabled=True)

        self.target_person = Person.objects.create_person('test@deomain.com')
        self.other_person = Person.objects.create_person('test2@fzejfzeji.fr')

        permission_names = ['view_authorization', 'add_authorization', 'change_authorization', 'delete_authorization']

        self.privileged_client.role.user_permissions.add(
            *(Permission.objects.get(codename=p) for p in permission_names)
        )

        self.scope1 = scopes.view_profile
        self.scope2 = scopes.edit_profile

        self.auth_target_oauth = models.Authorization.objects.create(
            person=self.target_person,
            client=self.oauth_client
        )
        self.auth_target_oauth.scopes = [self.scope1.name, self.scope2.name]

        self.auth_other_oauth = models.Authorization.objects.create(
            person=self.other_person,
            client=self.oauth_client
        )
        self.auth_other_oauth.scopes = [self.scope1.name]

    def test_cannot_see_authorizations_while_unauthenticated(self):
        response = self.client.get('/legacy/authorizations/')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_persons_can_see_own_when_unprivileged(self):
        self.client.force_login(self.target_person.role)
        response = self.client.get('/legacy/authorizations/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            urlparse(response.data[0]['person']).path,
            reverse('legacy:person-detail', kwargs={'pk': self.target_person.pk})
        )

    def test_can_see_all_with_privileges(self):
        self.client.force_login(self.privileged_client.role)
        response = self.client.get('/legacy/authorizations/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        obj_urls = [
            (reverse('legacy:person-detail', kwargs={'pk': a.person.pk}),
             reverse('legacy:client-detail', kwargs={'pk': a.client.pk}))
            for a in [self.auth_target_oauth, self.auth_other_oauth]
        ]

        self.assertCountEqual(
            [tuple(urlparse(url).path for url in [a['person'], a['client']]) for a in response.data],
            obj_urls
        )

    def test_person_can_modify_own_when_unprivileged(self):
        self.client.force_login(self.target_person.role)
        response = self.client.patch(
            '/legacy/authorizations/%d/' % self.auth_target_oauth.pk,
            data={'scopes': [scopes.view_profile.name]}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.auth_target_oauth.refresh_from_db()

        self.assertCountEqual(self.auth_target_oauth.scopes, [self.scope1.name])

    def test_cannot_modify_other_than_own_when_unprivileged(self):
        self.client.force_login(self.target_person.role)
        response = self.client.patch(
            '/legacy/authorizations/%d/' % self.auth_other_oauth.pk,
            data={'scopes': ['scope2']}
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_can_delete_own(self):
        self.client.force_login(self.target_person.role)
        response = self.client.delete('/legacy/authorizations/%d/' % self.auth_target_oauth.pk)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_cannot_delete_other_than_own(self):
        self.client.force_login(self.target_person.role)
        response = self.client.delete('/legacy/authorizations/%d/' % self.auth_other_oauth.pk)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
