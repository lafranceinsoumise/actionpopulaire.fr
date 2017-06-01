from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import list_route
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly

from lib.pagination import LegacyPaginator
from lib.permissions import RestrictViewPermissions, HasSpecificPermissions
from authentication.models import Role

from . import serializers, models


class HasViewClientPermission(HasSpecificPermissions):
    permissions = ['clients.view_client']


class LegacyClientViewSet(ModelViewSet):
    permission_classes = (RestrictViewPermissions,)
    serializer_class = serializers.LegacyClientSerializer
    queryset = models.Client.objects.all()
    pagination_class = LegacyPaginator

    def get_queryset(self):
        if not self.request.user.has_perm('clients.view_client'):
            if hasattr(self.request.user, 'type') and self.request.user.type == Role.CLIENT_ROLE:
                return self.queryset.filter(pk=self.request.user.client.pk)
            else:
                return self.queryset.none()
        return super(LegacyClientViewSet, self).get_queryset()

    @list_route(methods=["POST"], permission_classes=[HasViewClientPermission])
    def authenticate_client(self, request):
        input_serializer = serializers.ClientAuthenticationSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        client = input_serializer.validated_data['client']

        # the serializer needs the request in the context to generate the URLs
        context = self.get_serializer_context()
        output_serializer = serializers.LegacyClientSerializer(instance=client, context=context)

        return Response(output_serializer.data)


class ScopeViewSet(ModelViewSet):
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly, )
    serializer_class = serializers.ScopeSerializer
    queryset = models.Scope.objects.all()


class AuthorizationViewSet(ModelViewSet):
    permission_classes = (RestrictViewPermissions, )
    serializer_class = serializers.AuthorizationSerializer
    queryset = models.Authorization.objects.all()

    def get_queryset(self):
        if not self.request.user.has_perm('clients.view_authorization'):
            if hasattr(self.request.user, 'type') and self.request.user.type == Role.PERSON_ROLE:
                return self.queryset.filter(person_id=self.request.user.person.pk)
            else:
                return self.queryset.none()
        return super(AuthorizationViewSet, self).get_queryset()
