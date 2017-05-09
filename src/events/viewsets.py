from rest_framework.viewsets import ModelViewSet
import django_filters

from lib.permissions import PermissionsOrReadOnly
from lib.pagination import LegacyPaginator
from lib.filters import LegacyDistanceFilter
from lib.views import NationBuilderViewMixin

from . import serializers, models


class EventFilterSet(django_filters.rest_framework.FilterSet):
    closeTo = LegacyDistanceFilter(name='coordinates', lookup_expr='distance_lte')
    after = django_filters.DateTimeFilter(name='start_time', lookup_expr='gte')
    before = django_filters.DateTimeFilter(name='start_time', lookup_expr='lte')
    path = django_filters.CharFilter(name='nb_path', lookup_expr='exact')

    class Meta:
        model = models.Event
        fields = ('contact_email', 'start_time', 'closeTo', 'path', )


class LegacyEventViewSet(NationBuilderViewMixin, ModelViewSet):
    """
    Legacy endpoint for events that imitates the endpoint from Eve Python
    """
    permission_classes = (PermissionsOrReadOnly,)
    pagination_class = LegacyPaginator
    serializer_class = serializers.LegacyEventSerializer
    queryset = models.Event.objects.all().select_related('calendar').prefetch_related('tags')
    filter_class = EventFilterSet


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
