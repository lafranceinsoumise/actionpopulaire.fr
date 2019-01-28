import json
from datetime import timedelta

from django.contrib.gis.geos import Polygon
from django.db.models import Case, When, Value, BooleanField, Q, Count
from django.utils.timezone import now
from django.utils.translation import ugettext as _
from django.utils.html import mark_safe
from django.views.generic import TemplateView, DetailView
from django.views.decorators import cache
from django.views.decorators.clickjacking import xframe_options_exempt
from rest_framework.generics import ListAPIView
from rest_framework.exceptions import ValidationError
import django_filters
from django_filters.rest_framework.backends import DjangoFilterBackend
from django.http import QueryDict, Http404

from ..events.models import Event, EventSubtype
from ..groups.models import SupportGroup, SupportGroupSubtype

from . import serializers


def parse_bounds(bounds):
    if not bounds:
        return None

    try:
        bbox = json.loads(bounds)
    except json.JSONDecodeError:
        return None

    if not len(bbox) == 4:
        return None

    try:
        bbox = [float(c) for c in bbox]
    except ValueError:
        return None

    if not (-180.0 <= bbox[0] < bbox[2] <= 180.0) or not (
        -90.0 <= bbox[1] < bbox[3] <= 90
    ):
        return None

    return bbox


class BBoxFilterBackend(object):
    error_message = _(
        "Le paramètre bbox devrait être un tableau de 4 flottants [lon1, lat1, lon2, lat2]."
    )

    def filter_queryset(self, request, queryset, view):
        if not "bbox" in request.query_params:
            return queryset

        bbox = request.query_params["bbox"]

        if bbox is None:
            raise ValidationError(self.error_message)

        bbox = Polygon.from_bbox(bbox)

        return queryset.filter(coordinates__intersects=bbox)


class FixedModelMultipleChoiceFilter(django_filters.ModelMultipleChoiceFilter):
    def get_filter_predicate(self, v):
        return {self.field_name: v}


class EventFilterSet(django_filters.rest_framework.FilterSet):
    subtype = FixedModelMultipleChoiceFilter(
        field_name="subtype", to_field_name="label", queryset=EventSubtype.objects.all()
    )
    include_past = django_filters.BooleanFilter(
        "start_time",
        label="Inclure les événements passés",
        method="filter_include_past",
    )

    def __init__(self, data=None, *args, **kwargs):
        if data is not None:
            data = data.copy()
            if data.get("include_past") is None:
                data["include_past"] = False

        super().__init__(data, *args, **kwargs)

    def filter_include_past(self, queryset, name, value):
        if not value:
            return queryset.upcoming()
        else:
            return queryset

    class Meta:
        model = Event
        fields = ("subtype", "include_past")


class EventsView(ListAPIView):
    serializer_class = serializers.MapEventSerializer
    filter_backends = (BBoxFilterBackend, DjangoFilterBackend)
    filterset_class = EventFilterSet
    authentication_classes = []

    def get_queryset(self):
        return (
            Event.objects.published()
            .filter(coordinates__isnull=False)
            .select_related("subtype")
        )[:5000]

    @cache.cache_control(max_age=300, public=True)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class GroupFilterSet(django_filters.rest_framework.FilterSet):
    subtype = FixedModelMultipleChoiceFilter(
        field_name="subtypes",
        to_field_name="label",
        queryset=SupportGroupSubtype.objects.all(),
    )

    class Meta:
        model = SupportGroup
        fields = ("subtype",)


class GroupsView(ListAPIView):
    serializer_class = serializers.MapGroupSerializer
    filter_backends = (BBoxFilterBackend, DjangoFilterBackend)
    filterset_class = GroupFilterSet
    queryset = (
        SupportGroup.objects.active()
        .filter(coordinates__isnull=False)
        .prefetch_related("subtypes")
    )
    authentication_classes = []

    @cache.cache_control(max_age=300, public=True)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return (
            SupportGroup.objects.active()
            .filter(coordinates__isnull=False)
            .prefetch_related("subtypes")
            .annotate(
                current_events_count=Count(
                    "organized_events",
                    filter=Q(
                        organized_events__start_time__range=(
                            now() - timedelta(days=62),
                            now() + timedelta(days=31),
                        ),
                        organized_events__visibility=Event.VISIBILITY_PUBLIC,
                    ),
                )
            )
        )


class MapViewMixin:
    @xframe_options_exempt
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @classmethod
    def get_type_information(cls, id, label):
        return {
            "id": id,
            "label": label,
            "color": cls.TYPES_INFO[id][0],
            "iconName": cls.TYPES_INFO[id][1],
        }

    @staticmethod
    def get_subtype_information(subtype):
        res = {
            "id": subtype.id,
            "label": subtype.label,
            "description": subtype.description,
            "type": subtype.type,
            "hideLabel": subtype.hide_text_label,
        }

        if subtype.icon:
            res["iconUrl"] = subtype.icon.url
            if subtype.icon_anchor_x is not None and subtype.icon_anchor_y is not None:
                res["iconAnchor"] = [subtype.icon_anchor_x, subtype.icon_anchor_y]
            else:
                res["iconAnchor"] = [subtype.icon.width // 2, subtype.icon.height // 2]

            if subtype.popup_anchor_y is not None:
                res["popupAnchor"] = -subtype.popup_anchor_y
            else:
                res["popupAnchor"] = -res["iconAnchor"][1]
        elif subtype.icon_name:
            res["iconName"] = subtype.icon_name
            res["color"] = subtype.color

        return res


class AbstractListMapView(MapViewMixin, TemplateView):
    subtype_model = None

    def get_context_data(self, **kwargs):
        subtypes = self.subtype_model.objects.all()

        params = QueryDict(mutable=True)

        subtype_label = self.request.GET.getlist("subtype")
        if subtype_label:
            subtypes = subtypes.filter(label__in=subtype_label)
            params.setlist("subtype", subtype_label)

        if self.request.GET.get("include_past"):
            params["include_past"] = "1"

        subtype_info = [self.get_subtype_information(st) for st in subtypes]
        types = self.subtype_model._meta.get_field("type").choices
        type_info = [self.get_type_information(id, str(label)) for id, label in types]

        bounds = parse_bounds(self.request.GET.get("bounds"))

        querystring = ("?" + params.urlencode()) if params else ""

        return super().get_context_data(
            type_config=mark_safe(json.dumps(type_info)),
            subtype_config=mark_safe(json.dumps(subtype_info)),
            bounds=json.dumps(bounds),
            querystring=mark_safe(querystring),
            **kwargs
        )


class AbstractSingleItemMapView(MapViewMixin, DetailView):
    def get_context_data(self, **kwargs):
        if self.object.coordinates is None:
            raise Http404()

        subtype = self.get_subtype()
        type_info = self.get_type_information(subtype.type, subtype.get_type_display())
        subtype_info = self.get_subtype_information(subtype)

        if "iconUrl" in subtype_info or "iconName" in subtype_info:
            icon_config = subtype_info
        else:
            icon_config = type_info

        return super().get_context_data(
            subtype_config=mark_safe(json.dumps(icon_config)),
            coordinates=mark_safe(json.dumps(self.object.coordinates.coords)),
            **kwargs
        )


class EventMapMixin:
    subtype_model = EventSubtype
    queryset = Event.objects.published()

    TYPES_INFO = {
        "G": ["#4a64ac", "comments"],
        "M": ["#e14b35", "bullhorn"],
        "A": ["#c2306c", "exclamation"],
        "O": ["#49b37d", "calendar"],
    }

    def get_subtype(self):
        return self.object.subtype


class GroupMapMixin:
    subtype_model = SupportGroupSubtype
    queryset = SupportGroup.objects.active()
    context_object_name = "group"

    TYPES_INFO = {
        "L": ["#4a64ac", "users"],
        "B": ["#49b37d", "book"],
        "F": ["#e14b35", "cog"],
        "P": ["#f4981e", "industry"],
    }

    def get_subtype(self):
        return self.object.subtypes.first()


class EventMapView(EventMapMixin, AbstractListMapView):
    template_name = "carte/events.html"


class GroupMapView(GroupMapMixin, AbstractListMapView):
    template_name = "carte/groups.html"


class SingleEventMapView(EventMapMixin, AbstractSingleItemMapView):
    template_name = "carte/single_event.html"


class SingleGroupMapView(GroupMapMixin, AbstractSingleItemMapView):
    template_name = "carte/single_group.html"
