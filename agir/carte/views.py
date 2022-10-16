import json
from collections import OrderedDict

import django_filters
from data_france.models import (
    Departement,
    Region,
    Commune,
    CirconscriptionLegislative,
    Canton,
)
from django.contrib.gis.db.models import Extent, MultiPolygonField, Union
from django.contrib.gis.geos import Polygon
from django.db.models import Count, Q
from django.db.models.functions import Cast
from django.http import QueryDict, Http404
from django.utils.decorators import method_decorator
from django.utils.html import mark_safe
from django.utils.translation import gettext as _
from django.views.decorators import cache
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic import TemplateView, DetailView
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView

from agir.lib.export import dict_to_camelcase
from agir.municipales.models import CommunePage
from . import serializers
from ..events.filters import EventFilter
from ..events.models import Event, EventSubtype
from ..groups.models import SupportGroup, SupportGroupSubtype
from ..groups.utils import is_active_group_filter
from ..lib.filters import FixedModelMultipleChoiceFilter
from ..lib.views import AnonymousAPIView

DATA_FRANCE_OBJECT_MODEL = OrderedDict(
    {
        "commune": Commune,
        "circo": CirconscriptionLegislative,
        "departement": Departement,
        "canton": Canton,
        "region": Region,
    }
)


def get_data_france_object_bounds(code_postal=None, **kwargs):
    if code_postal:
        zips = code_postal if isinstance(code_postal, list) else [code_postal]
        kwargs["commune"] = list(
            Commune.objects.exclude(geometry__isnull=True)
            .filter(
                Q(codes_postaux__code__in=zips)
                | Q(commune_parent__codes_postaux__code__in=zips)
            )
            .values_list("code", flat=True)
        )

    for key, model in DATA_FRANCE_OBJECT_MODEL.items():
        codes = kwargs.get(key, None)
        if codes:
            codes = codes if isinstance(codes, list) else [codes]
            qs = model.objects.exclude(geometry__isnull=True).filter(code__in=codes)
            if qs.exists():
                return qs.annotate(
                    poly=Union(
                        Cast(
                            "geometry", output_field=MultiPolygonField(geography=False)
                        )
                    )
                ).aggregate(bbox=Extent("poly"))["bbox"]

    return None


def parse_bounds(bounds):
    if not bounds:
        return None

    try:
        bbox = json.loads(bounds)
    except json.JSONDecodeError as e:
        print(e)
        return None

    if isinstance(bbox, dict):
        bbox = get_data_france_object_bounds(**bbox)

    if not bbox or not len(bbox) == 4:
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


class EventsView(AnonymousAPIView, ListAPIView):
    permission_classes = ()
    serializer_class = serializers.MapEventSerializer
    filter_backends = (BBoxFilterBackend, DjangoFilterBackend)
    filterset_class = EventFilter
    queryset = (
        Event.objects.listed()
        .filter(coordinates__isnull=False)
        .select_related("subtype")
    )

    @method_decorator(cache.cache_page(300))
    @method_decorator(cache.cache_control(public=True))
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


class GroupsView(AnonymousAPIView, ListAPIView):
    permission_classes = ()
    serializer_class = serializers.MapGroupSerializer
    filter_backends = (BBoxFilterBackend, DjangoFilterBackend)
    filterset_class = GroupFilterSet

    @method_decorator(cache.cache_page(300))
    @method_decorator(cache.cache_control(public=True))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return (
            SupportGroup.objects.active()
            .filter(coordinates__isnull=False)
            .prefetch_related("subtypes")
            .annotate(is_active=Count("id", filter=is_active_group_filter()))
        )


class MapViewMixin:
    @xframe_options_exempt
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @classmethod
    def get_type_information(cls, id, label):
        return {"id": id, "label": label}


class CommuneMixin:
    def get(self, request, *args, **kwargs):
        try:
            self.commune = CommunePage.objects.get(
                code_departement=kwargs["departement"], slug=kwargs["nom"]
            )
        except CommunePage.DoesNotExist:
            raise Http404()

        return super().get(request, *args, **kwargs)

    def active_group_in_commune_exists(self):
        return SupportGroup.objects.filter(
            is_active_group_filter(), coordinates__intersects=self.commune.coordinates
        ).exists()

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            commune=self.commune.coordinates.json,
            hide_search=True,
            hide_active_control=not self.active_group_in_commune_exists(),
            **kwargs
        )


class AbstractListMapView(MapViewMixin, TemplateView):
    subtype_model = None

    def get_context_data(self, **kwargs):
        subtypes = self.subtype_model.objects.all()

        params = QueryDict(mutable=True)

        subtype_label = self.request.GET.getlist("subtype")
        if subtype_label:
            params.setlist("subtype", subtype_label)

        if self.request.GET.get("include_past"):
            params["include_past"] = "1"

        if self.request.GET.get("include_hidden"):
            params["include_hidden"] = "1"

        subtype_info = [
            dict_to_camelcase(st.get_subtype_information()) for st in subtypes
        ]
        types = self.subtype_model._meta.get_field("type").choices
        type_info = [
            dict_to_camelcase(self.get_type_information(id, str(label)))
            for id, label in types
        ]

        bounds = parse_bounds(self.request.GET.get("bounds"))

        query_params = ("?" + params.urlencode()) if params else ""

        controls = {}

        if (
            self.request.GET.get("no_controls")
            and self.request.GET.get("no_controls") == "1"
        ):
            controls = {"search": False, "active": False, "layers": False}

        return super().get_context_data(
            type_config=type_info,
            subtype_config=subtype_info,
            bounds=bounds,
            query_params=mark_safe(query_params),
            controls=controls,
            **kwargs
        )


class AbstractSingleItemMapView(MapViewMixin, DetailView):
    def get_context_data(self, **kwargs):
        if self.object.coordinates is None:
            raise Http404()

        subtype = self.get_subtype()
        icon_config = dict_to_camelcase(subtype.get_subtype_information())

        return super().get_context_data(
            subtype_config=icon_config,
            coordinates=self.object.coordinates.coords,
            **kwargs
        )


class EventMapMixin:
    subtype_model = EventSubtype
    queryset = Event.objects.listed()

    def get_subtype(self):
        return self.object.subtype


class GroupMapMixin:
    subtype_model = SupportGroupSubtype
    queryset = SupportGroup.objects.active()
    context_object_name = "group"

    def get_subtype(self):
        return self.object.subtypes.order_by("-icon", "-icon_name", "created").first()


class EventMapView(EventMapMixin, AbstractListMapView):
    template_name = "carte/events.html"


class GroupMapView(GroupMapMixin, AbstractListMapView):
    template_name = "carte/groups.html"


class CommuneEventMapView(CommuneMixin, EventMapView):
    pass


class CommuneGroupMapView(CommuneMixin, GroupMapView):
    pass


class SingleEventMapView(EventMapMixin, AbstractSingleItemMapView):
    template_name = "carte/single_event.html"
    queryset = Event.objects.all()

    def get(self, request, *args, **kwargs):
        if not request.user.has_perm("events.view_event", self.get_object()):
            raise Http404("Cette page n'existe pas.")
        return super().get(request, *args, **kwargs)


class SingleGroupMapView(GroupMapMixin, AbstractSingleItemMapView):
    template_name = "carte/single_group.html"
