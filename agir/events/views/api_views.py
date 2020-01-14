from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView

from agir.events.filters import EventAPIFilterSet
from agir.events.models import Event
from agir.events.serializers import EventSerializer
from agir.lib.pagination import APIPaginator

__all__ = ["EventSearchAPIView"]


class EventSearchAPIView(ListAPIView):
    queryset = Event.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = EventAPIFilterSet
    serializer_class = EventSerializer
    pagination_class = APIPaginator
