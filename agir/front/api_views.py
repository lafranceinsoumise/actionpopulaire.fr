from rest_framework.generics import (
    RetrieveAPIView,
)
from rest_framework import permissions
from rest_framework.response import Response

from agir.events.models import Event
from agir.groups.models import SupportGroup
from agir.groups.serializers import SupportGroupDetailSerializer
from agir.events.serializers import EventSerializer


class SearchAPIView(RetrieveAPIView):
    """Rechercher et lister des groupes et des événéments"""

    permission_classes = (permissions.AllowAny,)

    def get(self, request, *args, **kwargs):

        q = request.GET.get("q", "")
        context = {"request": self.request}

        support_groups = SupportGroup.objects.active().search(q).order_by("name")[:20]
        events = Event.objects.filter(
            visibility=Event.VISIBILITY_PUBLIC, do_not_list=False
        )[:30]
        result_count = int(support_groups.count()) + int(events.count())

        group_serializer = SupportGroupDetailSerializer(
            data=support_groups, context=context, many=True
        )
        group_serializer.is_valid()

        event_serializer = EventSerializer(data=events, context=context, many=True)
        event_serializer.is_valid()

        return Response(
            {
                "query": q,
                "result_count": result_count,
                "groups": group_serializer.data,
                "events": event_serializer.data,
            }
        )
