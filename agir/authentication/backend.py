from django.urls import resolve
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import base36_to_int
from django.utils.crypto import constant_time_compare
from django.conf import settings
from django.core.exceptions import ValidationError
from urllib.parse import urlparse


from agir.people.models import Person
from agir.authentication.backend_mixins import GetRoleMixin


class ConnectionTokenGenerator(PasswordResetTokenGenerator):
    """Strategy object used to generate and check tokens used for connection"""
    key_salt = 'front.backend.ConnectionTokenGenerator'

    def _make_hash_value(self, user, timestamp):
        # le hash n'est basé que sur l'ID de l'utilisateur et le timestamp
        return (
            str(user.pk) + str(timestamp)
        )

    def check_token(self, user, token):
        """
        Check that a connection token is correct for a given user.
        """
        if not (user and token):
            return False
        # Parse the token
        try:
            ts_b36, hash = token.split("-")
        except ValueError:
            return False

        try:
            ts = base36_to_int(ts_b36)
        except ValueError:
            return False

        # Check that the timestamp/uid has not been tampered with
        if not constant_time_compare(self._make_token_with_timestamp(user, ts), token):
            return False

        # Check the timestamp is within limit
        if (self._num_days(self._today()) - ts) > settings.CONNECTION_LINK_VALIDITY:
            return False

        return True


token_generator = ConnectionTokenGenerator()


class OAuth2Backend(GetRoleMixin):
    prefetch = ['person']

    def authenticate(self, profile_url=None):
        if profile_url:
            path = urlparse(profile_url).path.replace('/legacy', '')

            match = resolve(path, urlconf='agir.api.routers')

            if match.view_name == 'person-detail':
                person_id = match.kwargs['pk']
                person = Person.objects.select_related('role').get(pk=person_id)

                return person.role if self.user_can_authenticate(person.role) else None

            # not authenticated
            return None


class MailLinkBackend(GetRoleMixin):
    prefetch = ['person']

    def authenticate(self, user_pk=None, code=None):
        if user_pk and code:
            try:
                user = Person.objects.select_related('role').get(pk=user_pk)
            except (Person.DoesNotExist, ValidationError):
                return None
            if token_generator.check_token(user, code) and self.user_can_authenticate(user.role):
                return user.role

        return None
