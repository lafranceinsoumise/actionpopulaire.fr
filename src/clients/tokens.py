import json
from uuid import UUID
from json.decoder import JSONDecodeError
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from api.redis import get_auth_redis_client
from .models import Client
from .scopes import scopes as all_scopes
from people.models import Person


class InvalidTokenException(Exception):
    pass


def token_redis_key(token):
    return '{prefix}{token}:payload'.format(
        prefix=settings.AUTH_REDIS_PREFIX,
        token=token
    )


class AccessToken():
    def __init__(self, token, client, person, scopes):
        self.token = token
        self.client = client
        self.person = person
        self.scopes = scopes

    def __eq__(self, other):
        return (
            self.token == other.token
        )

    @classmethod
    def get_token(cls, token):
        client = get_auth_redis_client()

        serialized_token_info = client.get(token_redis_key(token))

        if serialized_token_info is None:
            raise InvalidTokenException()

        try:
            token_info = json.loads(serialized_token_info)
        except (UnicodeDecodeError, JSONDecodeError):
            raise InvalidTokenException()

        if 'clientId' not in token_info or 'userId' not in token_info:
            raise InvalidTokenException()

        client_id = token_info['clientId']
        person_id = token_info['userId']
        scope_names = token_info['scope']

        try:
            client = Client.objects.get_by_natural_key(client_id)
            person = Person.objects.select_related('role').get(pk=UUID(person_id))

        except (ObjectDoesNotExist, ValueError):
            raise InvalidTokenException()

        def is_scope_valid(scope):
            return (scope.name in client.scopes and scope.name in scope_names)
        # not too bad if ones of the scopes was deleted / also filter on scopes allowed for client
        scopes = list(filter(is_scope_valid, all_scopes))

        if not scopes:
            raise InvalidTokenException()

        return AccessToken(token, client, person, scopes)
