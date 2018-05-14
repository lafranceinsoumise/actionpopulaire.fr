from rest_framework.permissions import BasePermission

from .tokens import AccessToken


class HasScopesPermission(BasePermission):
    scopes = []

    def has_permission(self, request, view):
        return has_scopes(request, self.scopes)


def has_scopes(request, scopes):
    if isinstance(request.auth, AccessToken):
        return set(scopes).issubset(request.auth.scopes)
    return True
