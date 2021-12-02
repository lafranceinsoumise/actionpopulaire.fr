import hmac
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from oauth2_provider.models import AccessToken

from rules.permissions import ObjectPermissionBackend as RulesObjectPermissionBackend
from django.utils.translation import gettext as _
from django.core.exceptions import PermissionDenied
from rest_framework import exceptions
from rest_framework.authentication import BasicAuthentication

from agir.clients.models import Client


class AccessTokenRulesPermissionBackend(RulesObjectPermissionBackend):
    """
    We extend django_rules permissions backend to shortcut django model backend
    in case the user is authenticated via a token
    """

    def has_perm(self, user_obj, perm, obj=None, *args, **kwargs):
        result = super().has_perm(user_obj, perm, obj)
        if (
            hasattr(user_obj, "token")
            and isinstance(user_obj.token, AccessToken)
            and result is False
        ):
            raise PermissionDenied()

        return result


class AccessTokenAuthentication(OAuth2Authentication):
    def authenticate(self, request):
        result = super().authenticate(request)

        if result is None:
            return None

        user, token = result
        user.token = token

        return user, token


class ClientAuthentication(BasicAuthentication):
    """
    Client authentication
    """

    def authenticate_credentials(self, client_id, client_secret, request=None):
        try:
            client = Client.objects.select_related("role").get(client_id=client_id)
        except Client.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            hmac.compare_digest(client_secret, "")
            raise exceptions.AuthenticationFailed(_("Invalid username/password."))

        if not hmac.compare_digest(client.client_secret, client_secret):
            raise exceptions.AuthenticationFailed(_("Invalid username/password."))

        return client.role, None
