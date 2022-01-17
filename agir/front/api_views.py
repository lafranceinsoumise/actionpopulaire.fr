from rest_framework.generics import (
    RetrieveAPIView,
)
from rest_framework import permissions

from agir.events.models import Event
from agir.groups.models import SupportGroup

from rest_framework.response import Response
from agir.groups.serializers import SupportGroupSerializer
from agir.events.serializers import EventSerializer


class SearchAPIView(RetrieveAPIView):
    """Rechercher et lister des groupes et des événéments"""

    permission_classes = (permissions.AllowAny,)
    querysets = {
        "upcoming_events": Event.objects.upcoming().filter(
            visibility=Event.VISIBILITY_PUBLIC, do_not_list=False
        ),
        "past_events": Event.objects.past().filter(
            visibility=Event.VISIBILITY_PUBLIC, do_not_list=False
        ),
        "support_groups": SupportGroup.objects.filter(published=True),
    }

    def get(self, request, *args, **kwargs):

        q = request.GET.get("q", "")
        # print("======= SEARCH EVENTS AND GROUPS", flush=True)
        # print(q, flush=True)

        support_groups = self.querysets["support_groups"]
        upcoming_events = self.querysets["upcoming_events"]
        past_events = self.querysets["past_events"]

        support_groups = support_groups.search(q).order_by("name")[:20]

        upcoming_events = upcoming_events.search(q).order_by(
            "-start_time", "-end_time"
        )[:20]

        past_events = past_events.search(q).order_by("-start_time", "-end_time")[:10]

        result_count = (
            int(support_groups.count())
            + int(upcoming_events.count())
            + int(past_events.count())
        )

        event_count = int(upcoming_events.count()) + int(past_events.count())

        group_serializer = SupportGroupSerializer(
            data=support_groups, context={"request": self.request}, many=True
        )
        group_serializer.is_valid()

        event_serializer = EventSerializer(
            data=past_events, context={"request": self.request}, many=True
        )
        event_serializer.is_valid()

        return Response(
            {
                "query": q,
                "result_count": result_count,
                "event_count": event_count,
                "groups": group_serializer.data,
                "events": event_serializer.data,
                # "upcoming_events": upcoming_events,
                # "past_events": past_events,
            }
        )
