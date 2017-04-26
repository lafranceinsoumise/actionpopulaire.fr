from django.utils.translation import ugettext as _
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, BasicAuthentication, get_authorization_header

from authentication.models import Role
from clients.tokens import AccessToken, InvalidTokenException
from clients.models import Client


class AccessTokenAuthentication(BaseAuthentication):
    """
    Access Token authentication 
    """
    def authenticate(self, request):
        """
        Returns a `Person` if a correct access token has been supplied.  Otherwise returns `None`.
        """
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != b'bearer':
            return None

        if len(auth) == 1:
            msg = _('Invalid basic header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid basic header. Credentials string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = AccessToken.get_token(auth[1].decode())
        except (InvalidTokenException, UnicodeDecodeError):
            msg = _('Token invalide.')
            raise exceptions.AuthenticationFailed(msg)

        return token.person, token


class ClientAuthentication(BasicAuthentication):
    """
    Client authentication
    """
    def authenticate_credentials(self, client_label, password):
        try:
            client = Client.objects.get_by_natural_key(client_label)
        except Client.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            Role().set_password(password)
            raise exceptions.AuthenticationFailed(_('Invalid username/password.'))

        if not client.role.check_password(password):
            raise exceptions.AuthenticationFailed(_('Invalid username/password.'))

        return client, None
