import django_filters
from data_france.models import CodePostal, Commune
from django.db.models import OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.utils.decorators import method_decorator
from django.views.decorators import cache
from django_countries import countries
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import (
    ListAPIView,
)
from rest_framework.response import Response

from agir.events.models import Event
from agir.events.serializers import EventListSerializer
from agir.groups.models import SupportGroup
from agir.groups.serializers import SupportGroupSearchResultSerializer
from agir.groups.utils.supportgroup import is_active_group_filter
from agir.lib.data import (
    code_postal_vers_code_departement,
    french_zipcode_to_country_code,
    departements_choices,
)
from agir.lib.rest_framework_permissions import IsActionPopulaireClientPermission


class SearchSupportGroupsAndEventsAPIView(ListAPIView):
    """Rechercher et lister des groupes et des événéments"""

    permission_classes = (IsActionPopulaireClientPermission,)
    event_queryset = Event.objects.listed().with_event_card_serializer_prefetch()
    group_queryset = (
        SupportGroup.objects.active()
        .prefetch_related("subtypes")
        .with_static_map_image()
    )

    RESULT_TYPE_GROUPS = "groups"
    RESULT_TYPE_EVENTS = "events"

    GROUP_FILTER_CERTIFIED = "CERTIFIED"
    GROUP_FILTER_NOT_CERTIFIED = "NOT_CERTIFIED"

    EVENT_FILTER_PAST = "PAST"
    EVENT_FILTER_UPCOMING = "UPCOMING"

    SORT_ALPHA_ASC = "ALPHA_ASC"
    SORT_ALPHA_DESC = "ALPHA_DESC"
    SORT_DATE_ASC = "DATE_ASC"
    SORT_DATE_DESC = "DATE_DESC"

    def get_serializer(self, serializer_class, *args, **kwargs):
        kwargs.setdefault("many", True)
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_groups(
        self,
        search_term,
        result_limit=20,
        group_type=None,
        sort=None,
        inactive=None,
        commune=None,
        country=None,
        **kwargs,
    ):
        groups = self.group_queryset

        # Filters
        if commune:
            groups = groups.for_commune(commune)
        elif country:
            groups = groups.filter(location_country=country)

        if group_type:
            if group_type == self.GROUP_FILTER_CERTIFIED:
                groups = groups.certified()
            elif group_type == self.GROUP_FILTER_NOT_CERTIFIED:
                groups = groups.uncertified()
            else:
                groups = groups.filter(type=group_type)

        if inactive != "1":
            groups = groups.filter(is_active_group_filter())

        # Query
        groups = groups.search(search_term).distinct()

        # Sort
        if sort == self.SORT_ALPHA_ASC:
            groups = groups.order_by("name")
        if sort == self.SORT_ALPHA_DESC:
            groups = groups.order_by("-name")

        groups = groups[:result_limit]

        groups_serializer = self.get_serializer(
            data=groups,
            serializer_class=SupportGroupSearchResultSerializer,
        )
        groups_serializer.is_valid()
        return groups_serializer.data

    def get_events(
        self,
        search_term,
        result_limit=20,
        event_type=None,
        schedule=None,
        sort=None,
        commune=None,
        country=None,
        **kwargs,
    ):
        events = self.event_queryset

        # Filters

        if commune:
            events = events.for_commune(commune)
        elif country:
            events = events.filter(location_country=country)

        if event_type:
            events = events.filter(subtype__type=event_type)
        if schedule == self.EVENT_FILTER_PAST:
            events = events.past()
        if schedule == self.EVENT_FILTER_UPCOMING:
            events = events.upcoming()

        # Query
        events = events.search(search_term).distinct()

        # Sort
        if sort is None or sort == self.SORT_DATE_DESC:
            sort = "-start_time"
        if sort == self.SORT_DATE_ASC:
            sort = "start_time"
        if sort == self.SORT_ALPHA_ASC:
            sort = "name"
        if sort == self.SORT_ALPHA_DESC:
            sort = "-name"

        events = events.order_by(sort)[:result_limit]

        events_serializer = self.get_serializer(
            data=events,
            serializer_class=EventListSerializer,
            fields=EventListSerializer.EVENT_CARD_FIELDS,
        )
        events_serializer.is_valid()

        return events_serializer.data

    def list(self, request, *args, **kwargs):
        query = request.GET.get("q", "")
        query = " ".join(query.split(" ")[:27])
        query_type = request.GET.get("type")
        results = {
            "query": query,
            "type": query_type,
            self.RESULT_TYPE_GROUPS: [],
            self.RESULT_TYPE_EVENTS: [],
        }

        base_filters = {
            "result_limit": 20 if query_type is not None else 3,
            "commune": request.GET.get("filters[commune]"),
            "country": request.GET.get("filters[country]"),
        }

        if query_type is None or query_type == self.RESULT_TYPE_GROUPS:
            group_filters = {
                "group_type": request.GET.get("filters[groupType]"),
                "sort": request.GET.get("filters[groupSort]"),
                "inactive": request.GET.get("filters[groupInactive]"),
            }
            results[self.RESULT_TYPE_GROUPS] = self.get_groups(
                query, **base_filters, **group_filters
            )

        if query_type is None or query_type == self.RESULT_TYPE_EVENTS:
            event_filters = {
                "event_type": request.GET.get("filters[eventType]"),
                "schedule": request.GET.get("filters[eventSchedule]"),
                "sort": request.GET.get("filters[eventSort]"),
            }
            results[self.RESULT_TYPE_EVENTS] = self.get_events(
                query,
                **base_filters,
                **event_filters,
            )

        return Response(results)


class CodePostaleFilterSet(django_filters.rest_framework.FilterSet):
    departement = django_filters.ChoiceFilter(
        field_name="departement",
        choices=departements_choices,
    )

    class Meta:
        model = CodePostal
        fields = ("departement", "code")


class CodePostalListAPIView(ListAPIView):
    permission_classes = (IsActionPopulaireClientPermission,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CodePostaleFilterSet
    queryset = (
        CodePostal.objects.all()
        .prefetch_related("communes")
        .annotate(
            departement=Coalesce(
                Subquery(
                    Commune.objects.filter(
                        composant__codes_postaux=OuterRef("pk")
                    ).values("departement__code")[:1]
                ),
                Subquery(
                    Commune.objects.filter(codes_postaux=OuterRef("pk")).values(
                        "departement__code"
                    )[:1]
                ),
            )
        )
    )

    @method_decorator(cache.cache_page(3600))
    @method_decorator(cache.cache_control(public=True))
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        result = []
        for code_postal in queryset:
            code = code_postal.as_dict()
            country = french_zipcode_to_country_code(code_postal.code)
            code["country"] = countries.name(country)
            code["departement"] = (
                code_postal.departement
                or code_postal_vers_code_departement(code_postal.code)
            )
            result.append(code)

        return Response(result)
