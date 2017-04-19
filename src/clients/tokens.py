import json
from uuid import UUID
from json.decoder import JSONDecodeError
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from api.redis import get_redis_client
from .models import Client, Scope
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

    @classmethod
    def get_token(cls, token):
        client = get_redis_client()

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
            person = Person.objects.get(UUID(person_id))

        except (ObjectDoesNotExist, ValueError):
            raise InvalidTokenException()

        # not too bad if ones of the scopes was deleted
        scopes = Scope.objects.get(name__in=scope_names)

        if not scopes:
            raise InvalidTokenException()

        return AccessToken(token, client, person, scopes)
