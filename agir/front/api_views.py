from rest_framework.generics import (
    ListAPIView,
)
from rest_framework import permissions
from rest_framework.response import Response

from agir.events.models import Event
from agir.groups.models import SupportGroup
from agir.groups.serializers import SupportGroupDetailSerializer
from agir.events.serializers import EventSerializer, EventListSerializer
from django.utils import timezone
import json
from django.conf import settings


CERTIFIED = "CERTIFIED"
NOT_CERTIFIED = "NOT_CERTIFIED"
ALPHA_ASC = "ALPHA_ASC"
ALPHA_DESC = "ALPHA_DESC"
DATE_ASC = "DATE_ASC"
DATE_DESC = "DATE_DESC"
PAST = "PAST"


class SearchSupportGroupsAndEventsAPIView(ListAPIView):
    """Rechercher et lister des groupes et des événéments"""

    RESULT_TYPE_GROUPS = "groups"
    RESULT_TYPE_EVENTS = "events"
    permission_classes = (permissions.AllowAny,)

    def get_serializer(self, serializer_class, *args, **kwargs):
        kwargs.setdefault("many", True)
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_groups(self, search_term, filters):

        groupType = filters.get("groupType", None)
        groupSort = filters.get("groupSort", None)

        groups = SupportGroup.objects.active()

        # Filter
        if groupType:
            if groupType == CERTIFIED:
                groups = groups.filter(
                    subtypes__label__in=settings.CERTIFIED_GROUP_SUBTYPES
                )
            elif groupType == NOT_CERTIFIED:
                groups = groups.exclude(
                    subtypes__label__in=settings.CERTIFIED_GROUP_SUBTYPES
                )
            else:
                groups = groups.filter(type=groupType)

        # Query
        groups = groups.search(search_term)

        # Sort
        if groupSort:
            if groupSort == ALPHA_ASC:
                groups = groups.order_by("name")
            if groupSort == ALPHA_DESC:
                groups = groups.order_by("-name")

        groups = groups[:20]

        groups_serializer = self.get_serializer(
            data=groups,
            serializer_class=SupportGroupDetailSerializer,
            fields=SupportGroupDetailSerializer.GROUP_CARD_FIELDS,
        )
        groups_serializer.is_valid()
        return groups_serializer.data

    def get_events(self, search_term, filters):

        eventType = filters.get("eventType", None)
        eventCategory = filters.get("eventCategory", None)
        eventSort = filters.get("eventSort", None)

        events = Event.objects.filter(
            visibility=Event.VISIBILITY_PUBLIC, do_not_list=False
        )

        # Filters
        if eventType:
            events = events.filter(subtype__type=eventType)
        if eventCategory:
            if eventCategory == PAST:
                events = events.filter(end_time__lte=timezone.now())
            else:
                events = events.filter(end_time__gte=timezone.now())

        # Query
        events = events.search(search_term)

        # Sort
        if eventSort:
            if eventSort == DATE_ASC:
                events = events.order_by("start_time")
            if eventSort == DATE_DESC:
                events = events.order_by("-start_time")
            if eventSort == ALPHA_ASC:
                events = events.order_by("name")
            if eventSort == ALPHA_DESC:
                events = events.order_by("-name")

        events = events[:20]

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
        filters = json.loads(request.GET.get("filters", "{}"))
        results = {"query": search_term}

        if type is None or type == self.RESULT_TYPE_GROUPS:
            results[self.RESULT_TYPE_GROUPS] = self.get_groups(search_term, filters)

        if type is None or type == self.RESULT_TYPE_EVENTS:
            results[self.RESULT_TYPE_EVENTS] = self.get_events(search_term, filters)

        return Response(results)
