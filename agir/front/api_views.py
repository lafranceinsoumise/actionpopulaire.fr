import json

from django.conf import settings
from django.utils import timezone
from rest_framework.generics import (
    ListAPIView,
)
from rest_framework.response import Response

from agir.events.models import Event
from agir.events.serializers import EventSerializer, EventListSerializer
from agir.groups.models import SupportGroup
from agir.groups.serializers import SupportGroupSearchResultSerializer

from agir.groups.utils import is_active_group_filter
from agir.lib.rest_framework_permissions import IsActionPopulaireClientPermission


class SearchSupportGroupsAndEventsAPIView(ListAPIView):
    """Rechercher et lister des groupes et des événéments"""

    permission_classes = (IsActionPopulaireClientPermission,)
    RESULT_TYPE_GROUPS = "groups"
    RESULT_TYPE_EVENTS = "events"
    GROUP_FILTER_CERTIFIED = "CERTIFIED"
    GROUP_FILTER_NOT_CERTIFIED = "NOT_CERTIFIED"
    SORT_ALPHA_ASC = "ALPHA_ASC"
    SORT_ALPHA_DESC = "ALPHA_DESC"
    SORT_DATE_ASC = "DATE_ASC"
    SORT_DATE_DESC = "DATE_DESC"
    EVENT_FILTER_PAST = "PAST"

    def get_serializer(self, serializer_class, *args, **kwargs):
        kwargs.setdefault("many", True)
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_groups(self, search_term, filters, result_limit=20):

        groupType = filters.get("groupType", None)
        groupSort = filters.get("groupSort", None)
        groupInactive = filters.get("groupInactive", None)
        country = filters.get("country", None)

        groups = (
            SupportGroup.objects.active()
            .prefetch_related("subtypes")
            .with_static_map_image()
        )

        # Filters
        if country:
            groups = groups.filter(location_country=country)

        if groupType:
            if groupType == self.GROUP_FILTER_CERTIFIED:
                groups = groups.filter(
                    subtypes__label__in=settings.CERTIFIED_GROUP_SUBTYPES
                )
            elif groupType == self.GROUP_FILTER_NOT_CERTIFIED:
                groups = groups.exclude(
                    subtypes__label__in=settings.CERTIFIED_GROUP_SUBTYPES
                )
            else:
                groups = groups.filter(type=groupType)

        if groupInactive != "1":
            groups = groups.filter(is_active_group_filter())

        # Query
        groups = groups.search(search_term).distinct()

        # Sort
        if groupSort:
            if groupSort == self.SORT_ALPHA_ASC:
                groups = groups.order_by("name")
            if groupSort == self.SORT_ALPHA_DESC:
                groups = groups.order_by("-name")

        groups = groups[:result_limit]

        groups_serializer = self.get_serializer(
            data=groups,
            serializer_class=SupportGroupSearchResultSerializer,
        )
        groups_serializer.is_valid()
        return groups_serializer.data

    def get_events(self, search_term, filters, result_limit=20):
        eventType = filters.get("eventType", None)
        eventCategory = filters.get("eventCategory", None)
        eventSort = filters.get("eventSort", self.SORT_DATE_ASC)
        country = filters.get("country", None)

        events = Event.objects.listed().with_serializer_prefetch(None)

        # Filters
        if country:
            events = events.filter(location_country=country)
        if eventType:
            events = events.filter(subtype__type=eventType)

        if eventCategory:
            if eventCategory == self.EVENT_FILTER_PAST:
                events = events.past()
            else:
                events = events.upcoming()

        # Query
        events = events.search(search_term).distinct()

        # Default: get upcoming events
        if not eventCategory and events.upcoming().count() >= result_limit:
            events = events.upcoming()

        # Sort
        if eventSort:
            if eventSort == self.SORT_DATE_ASC:
                events = events.order_by("start_time")
            if eventSort == self.SORT_DATE_DESC:
                events = events.order_by("-start_time")
            if eventSort == self.SORT_ALPHA_ASC:
                events = events.order_by("name")
            if eventSort == self.SORT_ALPHA_DESC:
                events = events.order_by("-name")

        events = events[:result_limit]

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
        results = {
            "query": search_term,
            self.RESULT_TYPE_GROUPS: [],
            self.RESULT_TYPE_EVENTS: [],
        }

        result_limit = 20 if type is not None else 3

        if type is None or type == self.RESULT_TYPE_GROUPS:
            results[self.RESULT_TYPE_GROUPS] = self.get_groups(
                search_term, filters, result_limit=result_limit
            )

        if type is None or type == self.RESULT_TYPE_EVENTS:
            results[self.RESULT_TYPE_EVENTS] = self.get_events(
                search_term, filters, result_limit=result_limit
            )

        return Response(results)
