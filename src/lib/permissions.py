from rest_framework import exceptions
from rest_framework.permissions import DjangoModelPermissions


class GlobalOrObjectPermissionsMixin(object):
    def get_required_object_permissions(self, method, model_cls):
        kwargs = {
            'app_label': model_cls._meta.app_label,
            'model_name': model_cls._meta.model_name
        }

        if method not in self.perms_map:
            raise exceptions.MethodNotAllowed(method)

        return [perm % kwargs for perm in self.object_perms_map[method]]

    def has_object_permission(self, request, view, obj):
        if hasattr(view, 'get_queryset'):
            queryset = view.get_queryset()
        else:
            queryset = getattr(view, 'queryset', None)

        assert queryset is not None, (
            'Cannot apply DjangoObjectPermissions on a view that '
            'does not set `.queryset` or have a `.get_queryset()` method.'
        )

        model_cls = queryset.model
        user = request.user

        perms = self.get_required_object_permissions(request.method, model_cls)

        return user.has_perms(perms) or user.has_perms(perms, obj)


class RestrictViewPermissions(GlobalOrObjectPermissionsMixin, DjangoModelPermissions):
    authenticated_users_only = True

    perms_map = {
        'GET': [],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': [],
        'PATCH': [],
        'DELETE': [],
    }

    object_perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': [],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }


class PermissionsOrReadOnly(GlobalOrObjectPermissionsMixin, DjangoModelPermissions):
    authenticated_users_only = False

    perms_map = {
        'GET': [],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': [],
        'PATCH': [],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }

    object_perms_map = {
        'GET': [],
        'OPTIONS': [],
        'HEAD': [],
        'POST': [],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': [],
    }
