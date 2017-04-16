from rest_framework.viewsets import ModelViewSet

from lib.pagination import LegacyPaginator

from . import serializers, models


class LegacyPersonViewSet(ModelViewSet):
    pagination_class = LegacyPaginator
    serializer_class = serializers.LegacyPersonSerializer
    queryset = models.Person.objects.all()
