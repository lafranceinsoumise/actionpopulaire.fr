from rest_framework.viewsets import ModelViewSet

from lib.pagination import LegacyPaginator

from . import serializers, models


class LegacyEventViewSet(ModelViewSet):
    """
    Legacy endpoint for events that imitates the endpoint from Eve Python
    """
    pagination_class = LegacyPaginator
    serializer_class = serializers.LegacyEventSerializer
    queryset = models.Event.objects.all().select_related('calendar').prefetch_related('tags')


class CalendarViewSet(ModelViewSet):
    """
    Calendar Viewset !
    """
    serializer_class = serializers.CalendarSerializer
    queryset = models.Calendar.objects.all()


class EventTagViewSet(ModelViewSet):
    """
    EventTag viewset
    """
    serializer_class = serializers.EventTagSerializer
    queryset = models.EventTag.objects.all()


class RSVPViewSet(ModelViewSet):
    """
    
    """

    serializer_class = serializers.RSVPSerializer
    queryset = models.RSVP.objects.select_related('event', 'person')
