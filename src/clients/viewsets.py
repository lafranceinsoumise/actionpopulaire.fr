from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import list_route

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
