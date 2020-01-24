from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView

from agir.events.filters import EventAPIFilter
from agir.events.models import Event
from agir.events.serializers import EventSerializer
from agir.lib.pagination import APIPaginator

__all__ = ["EventSearchAPIView"]


class EventSearchAPIView(ListAPIView):
    queryset = Event.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = EventAPIFilter
    serializer_class = EventSerializer
    pagination_class = APIPaginator
