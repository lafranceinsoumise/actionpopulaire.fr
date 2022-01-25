from rest_framework.generics import (
    RetrieveAPIView,
)
from rest_framework import permissions
from rest_framework.response import Response

from agir.events.models import Event
from agir.groups.models import SupportGroup
from agir.groups.serializers import SupportGroupDetailSerializer
from agir.events.serializers import EventSerializer, EventListSerializer

TYPE_ALL = "all"
TYPE_EVENTS = "evenements"
TYPE_GROUPS = "groups"

class SearchSupportGroupsAndEventsAPIView(RetrieveAPIView):
    """Rechercher et lister des groupes et des événéments"""

    permission_classes = (permissions.AllowAny,)
    type = TYPE_ALL

    def get(self, request, *args, **kwargs):

        q = request.GET.get("q", "")
        context = {"request": self.request}
        group_results = []
        event_results = []

        if self.type in [TYPE_GROUPS, TYPE_ALL]:
            support_groups = SupportGroup.objects.active().search(q)[:20]
            group_serializer = SupportGroupDetailSerializer(
                data=support_groups,
                context=context,
                many=True,
                fields=SupportGroupDetailSerializer.GROUP_CARD_FIELDS,
            )
            group_serializer.is_valid()
            group_results = group_serializer.data

        if self.type in [TYPE_EVENTS, TYPE_ALL]:
            events = Event.objects.filter(
                visibility=Event.VISIBILITY_PUBLIC, do_not_list=False
            ).search(q)[:30]
            event_serializer = EventSerializer(
                data=events,
                context=context,
                many=True,
                fields=EventListSerializer.EVENT_CARD_FIELDS,
            )
            event_serializer.is_valid()
            event_results = event_serializer.data

        return Response(
            {
                "query": q,
                "groups": group_results,
                "events": event_results,
            }
        )


class SearchSupportGroupsAPIView(SearchSupportGroupsAndEventsAPIView):
    type = TYPE_GROUPS


class SearchSupportEventsAPIView(SearchSupportGroupsAndEventsAPIView):
    type = TYPE_EVENTS
