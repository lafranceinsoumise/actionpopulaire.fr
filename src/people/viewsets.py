from rest_framework.viewsets import ModelViewSet

from lib.pagination import LegacyPaginator

from . import serializers, models


class LegacyPersonViewSet(ModelViewSet):
    """
    Legacy endpoint for people that imitates the endpoint from Eve Python
    """
    pagination_class = LegacyPaginator
    serializer_class = serializers.LegacyPersonSerializer
    queryset = models.Person.objects.all()
