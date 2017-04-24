from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import DjangoModelPermissions

from . import serializers, models


class LegacyClientViewSet(ModelViewSet):
    permission_classes = (DjangoModelPermissions,)
    serializer_class = serializers.LegacyClientSerializer
    queryset = models.Client.objects.all()
