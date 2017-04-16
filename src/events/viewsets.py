from rest_framework.viewsets import ModelViewSet

from lib.pagination import LegacyPaginator

from . import serializers, models


class LegacyEventViewSet(ModelViewSet):
    """
    Legacy endpoint for events that imitates the endpoint from Eve Python
    """
    pagination_class = LegacyPaginator
    serializer_class = serializers.LegacyEventSerializer
    queryset = models.Event.objects.all()


class CalendarViewSet(ModelViewSet):
    """
    Calendar Viewset !
    """
    serializer_class = serializers.CalendarSerializer
    queryset = models.Calendar.objects.all()
