from rest_framework.generics import (
    RetrieveAPIView,
)
from rest_framework import permissions
from rest_framework.response import Response

from agir.events.models import Event
from agir.groups.models import SupportGroup
from agir.groups.serializers import SupportGroupDetailSerializer
from agir.events.serializers import EventSerializer, EventListSerializer


class SearchSupportGroupsAndEventsAPIView(RetrieveAPIView):
    """Rechercher et lister des groupes et des événéments"""

    permission_classes = (permissions.AllowAny,)

    def get(self, request, *args, **kwargs):

        q = request.GET.get("q", "")
        context = {"request": self.request}

        support_groups = SupportGroup.objects.active().search(q)[:20]
        events = Event.objects.filter(
            visibility=Event.VISIBILITY_PUBLIC, do_not_list=False
        ).search(q)[:30]

        group_serializer = SupportGroupDetailSerializer(
            data=support_groups,
            context=context,
            many=True,
            fields=SupportGroupDetailSerializer.GROUP_CARD_FIELDS,
        )
        group_serializer.is_valid()

        event_serializer = EventSerializer(
            data=events,
            context=context,
            many=True,
            fields=EventListSerializer.EVENT_CARD_FIELDS,
        )
        event_serializer.is_valid()

        return Response(
            {
                "query": q,
                "groups": group_serializer.data,
                "events": event_serializer.data,
            }
        )
