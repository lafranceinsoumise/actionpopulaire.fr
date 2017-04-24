from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly, DjangoObjectPermissions


class PermissionsOrReadOnly(DjangoModelPermissionsOrAnonReadOnly, DjangoObjectPermissions):
    pass


class PermissionsOrIsResource(DjangoObjectPermissions):
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user == obj:
            return True

        return super(PermissionsOrIsResource, self).has_object_permission(request, view, obj)
