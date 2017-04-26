from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import DjangoModelPermissions

from lib.pagination import LegacyPaginator
from . import serializers, models


class LegacyClientViewSet(ModelViewSet):
    permission_classes = (DjangoModelPermissions,)
    serializer_class = serializers.LegacyClientSerializer
    queryset = models.Client.objects.all()
    pagination_class = LegacyPaginator

    def get_queryset(self):
        if not self.request.user.has_perm('clients.view_client'):
            return self.queryset.filter(pk=self.request.user.pk)
        return super(LegacyClientViewSet, self).get_queryset()
