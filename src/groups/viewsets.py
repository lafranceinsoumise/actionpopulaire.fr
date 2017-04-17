from rest_framework.viewsets import ModelViewSet

from lib.pagination import LegacyPaginator

from . import serializers, models


class LegacySupportGroupViewSet(ModelViewSet):
    """
    Legacy endpoint for events that imitates the endpoint from Eve Python
    """
    pagination_class = LegacyPaginator
    serializer_class = serializers.LegacySupportGroupSerializer
    queryset = models.SupportGroup.objects.all().prefetch_related('tags')


class SupportGroupTagViewSet(ModelViewSet):
    """
    EventTag viewset
    """
    serializer_class = serializers.SupportGroupTagSerializer
    queryset = models.SupportGroupTag.objects.all()
