from urllib.parse import urlparse

from django.contrib.auth import get_user
from django.http import QueryDict
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from agir.authentication.backend import token_generator
from agir.events.models import Event
from agir.groups.models import SupportGroup
from agir.people.models import Person


class AuthenticationTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_person('test@test.com', )

        self.soft_backend = 'agir.authentication.backend.MailLinkBackend'

    def test_can_connect_with_query_params(self):
        p = self.person.pk
        code = token_generator.make_token(self.person)

        response = self.client.get(reverse('volunteer'), data={'p': p, 'code': code})

        self.assertRedirects(response, reverse('volunteer'))
        self.assertEqual(get_user(self.client), self.person.role)

    def test_can_access_soft_login_while_already_connected(self):
        self.client.force_login(self.person.role, self.soft_backend)

        response = self.client.get(reverse('volunteer'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cannot_access_hard_login_page_while_soft_logged_in(self):
        self.client.force_login(self.person.role, self.soft_backend)

        response = self.client.get(reverse('create_group'))

        self.assertRedirects(
            response, reverse('oauth_redirect_view') + '?next=' + reverse('create_group'),
            target_status_code=status.HTTP_302_FOUND
        )

    def test_unsubscribe_redirects_to_message_preferences_when_logged(self):
        message_preferences_path = reverse('message_preferences')
        unsubscribe_path = reverse('unsubscribe')

        self.client.force_login(self.person.role)
        response = self.client.get(unsubscribe_path)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        target_url = urlparse(response.url)
        self.assertEqual(target_url.path, message_preferences_path)


class AuthorizationTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_person('test@test.com')

        now = timezone.now()
        day = timezone.timedelta(days=1)
        hour = timezone.timedelta(hours=1)

        self.event = Event.objects.create(
            name="event",
            start_time=now + day,
            end_time=now + day + hour,
        )

        self.group = SupportGroup.objects.create(
            name="group",
        )

    def test_redirect_when_unauth(self):
        for url in ['/', '/evenements/creer/', '/groupes/creer/',
                    '/evenements/%s/modifier/' % self.event.pk, '/groupes/%s/modifier/' % self.group.pk]:
            response = self.client.get(url)
            query = QueryDict(mutable=True)
            query['next'] = url
            self.assertRedirects(response, '/authentification/?%s' % query.urlencode(safe='/'), target_status_code=302)

    def test_403_when_editing_event(self):
        self.client.force_login(self.person.role)

        response = self.client.get('/evenements/%s/modifier/' % self.event.pk)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.post('/evenements/%s/modifier/' % self.event.pk)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_403_when_editing_group(self):
        self.client.force_login(self.person.role)

        response = self.client.get('/groupes/%s/modifier/' % self.group.pk)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.post('/groupes/%s/modifier/' % self.group.pk)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_oauth_backend(self):
        from agir.authentication.backend import OAuth2Backend
        backend = OAuth2Backend()
        profile_url = reverse('legacy:person-detail', kwargs={'pk': self.person.pk})

        self.assertEqual(self.person.role, backend.authenticate(profile_url=profile_url))
