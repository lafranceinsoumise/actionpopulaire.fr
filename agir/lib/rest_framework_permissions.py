from oauth2_provider.models import AccessToken
from rest_framework import exceptions
from rest_framework.permissions import DjangoModelPermissions, BasePermission
from django.core.exceptions import PermissionDenied

from agir.clients.scopes import get_required_scopes


def get_class_from_view(view):
    if hasattr(view, "get_queryset"):
        queryset = view.get_queryset()
    else:
        queryset = getattr(view, "queryset", None)

    assert queryset is not None, (
        "Cannot apply DjangoObjectPermissions on a view that "
        "does not set `.queryset` or have a `.get_queryset()` method."
    )

    return queryset.model


class ScopePermissionsMixin(object):
    def has_permission(self, request, view):
        if isinstance(request.auth, AccessToken):
            model_cls = get_class_from_view(view)
            required_permissions = self.get_required_permissions(
                request.method, model_cls
            )
            required_scopes = set(
                scope.name
                for permission in required_permissions
                for scope in get_required_scopes(permission)
            )

            if required_scopes and not request.auth.allow_scopes(required_scopes):
                raise PermissionDenied("Incorrect scopes")

        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        if isinstance(request.auth, AccessToken):
            model_cls = get_class_from_view(view)
            required_permissions = self.get_required_object_permissions(
                request.method, model_cls
            )
            required_scopes = set(
                scope.name
                for permission in required_permissions
                for scope in get_required_scopes(permission)
            )

            if required_scopes and not request.auth.allow_scopes(required_scopes):
                raise PermissionDenied("Incorrect scopes")
        return super().has_object_permission(request, view, obj)


class GlobalOrObjectPermissionsMixin(object):
    def get_required_object_permissions(self, method, model_cls):
        kwargs = {
            "app_label": model_cls._meta.app_label,
            "model_name": model_cls._meta.model_name,
        }

        if method not in self.perms_map:
            raise exceptions.MethodNotAllowed(method)

        return [perm % kwargs for perm in self.object_perms_map[method]]

    def has_object_permission(self, request, view, obj):
        model_cls = get_class_from_view(view)
        user = request.user
        perms = self.get_required_object_permissions(request.method, model_cls)

        return user.has_perms(perms) or user.has_perms(perms, obj)


class GlobalOnlyPermissions(ScopePermissionsMixin, DjangoModelPermissions):
    perms_map = {
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "OPTIONS": ["%(app_label)s.view_%(model_name)s"],
        "HEAD": ["%(app_label)s.view_%(model_name)s"],
        "POST": ["%(app_label)s.add_%(model_name)s"],
        "PUT": ["%(app_label)s.change_%(model_name)s"],
        "PATCH": ["%(app_label)s.change_%(model_name)s"],
        "DELETE": ["%(app_label)s.delete_%(model_name)s"],
    }


class GlobalOrObjectPermissions(
    ScopePermissionsMixin, GlobalOrObjectPermissionsMixin, DjangoModelPermissions
):
    authenticated_users_only = False

    perms_map = {
        "GET": [],
        "OPTIONS": [],
        "HEAD": [],
        "POST": ["%(app_label)s.add_%(model_name)s"],
        "PUT": [],
        "PATCH": [],
        "DELETE": [],
    }

    object_perms_map = {
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "OPTIONS": [],
        "HEAD": [],
        "POST": [],
        "PUT": ["%(app_label)s.change_%(model_name)s"],
        "PATCH": ["%(app_label)s.change_%(model_name)s"],
        "DELETE": ["%(app_label)s.delete_%(model_name)s"],
    }


class GlobalOrObjectPermissionOrReadOnly(
    ScopePermissionsMixin, GlobalOrObjectPermissionsMixin, DjangoModelPermissions
):
    authenticated_users_only = False

    perms_map = {
        "GET": [],
        "OPTIONS": [],
        "HEAD": [],
        "POST": ["%(app_label)s.add_%(model_name)s"],
        "PUT": [],
        "PATCH": [],
        "DELETE": ["%(app_label)s.delete_%(model_name)s"],
    }

    object_perms_map = {
        "GET": [],
        "OPTIONS": [],
        "HEAD": [],
        "POST": [],
        "PUT": ["%(app_label)s.change_%(model_name)s"],
        "PATCH": ["%(app_label)s.change_%(model_name)s"],
        "DELETE": [],
    }


class HasSpecificPermissions(BasePermission):
    permissions = []

    def has_permission(self, request, view):
        return request.user.has_perms(self.permissions)


class IsPersonPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.person is not None
