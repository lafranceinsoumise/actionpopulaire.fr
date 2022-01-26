from rest_framework.generics import (
    ListAPIView,
)
from rest_framework import permissions
from rest_framework.response import Response

from agir.events.models import Event
from agir.groups.models import SupportGroup
from agir.groups.serializers import SupportGroupDetailSerializer
from agir.events.serializers import EventSerializer, EventListSerializer


class SearchSupportGroupsAndEventsAPIView(ListAPIView):
    """Rechercher et lister des groupes et des événéments"""

    RESULT_TYPE_GROUPS = "groups"
    RESULT_TYPE_EVENTS = "events"
    permission_classes = (permissions.AllowAny,)

    def get_serializer(self, serializer_class, *args, **kwargs):
        kwargs.setdefault("many", True)
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_groups(self, search_term):
        groups = SupportGroup.objects.active().search(search_term)[:20]
        groups_serializer = self.get_serializer(
            data=groups,
            serializer_class=SupportGroupDetailSerializer,
            fields=SupportGroupDetailSerializer.GROUP_CARD_FIELDS,
        )
        groups_serializer.is_valid()
        return groups_serializer.data

    def get_events(self, search_term):
        events = Event.objects.filter(
            visibility=Event.VISIBILITY_PUBLIC, do_not_list=False
        ).search(search_term)[:30]
        events_serializer = self.get_serializer(
            data=events,
            serializer_class=EventSerializer,
            fields=EventListSerializer.EVENT_CARD_FIELDS,
        )
        events_serializer.is_valid()
        return events_serializer.data

    def list(self, request, *args, **kwargs):
        search_term = request.GET.get("q", "")
        type = request.GET.get("type")
        results = {"query": search_term}

        if type is None or type == self.RESULT_TYPE_GROUPS:
            results[self.RESULT_TYPE_GROUPS] = self.get_groups(search_term)

        if type is None or type == self.RESULT_TYPE_EVENTS:
            results[self.RESULT_TYPE_EVENTS] = self.get_events(search_term)

        return Response(results)
