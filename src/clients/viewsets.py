from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import DjangoModelPermissions

from lib.pagination import LegacyPaginator
from authentication.models import Role

from . import serializers, models


class LegacyClientViewSet(ModelViewSet):
    permission_classes = (DjangoModelPermissions,)
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
