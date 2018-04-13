import json
from django.contrib.gis.geos import Polygon
from django.utils.translation import ugettext as _
from django.utils.html import mark_safe
from django.views.generic import TemplateView, DetailView
from django.views.decorators import cache
from django.views.decorators.clickjacking import xframe_options_exempt
from rest_framework.generics import ListAPIView
from rest_framework.exceptions import ValidationError
import django_filters
from django_filters.rest_framework.backends import DjangoFilterBackend
from django.http import QueryDict


from events.models import Event, EventSubtype
from groups.models import SupportGroup, SupportGroupSubtype

from . import serializers


class BBoxFilterBackend(object):
    error_message = _("le paramètre bbox devrait être un tableau de 4 flottants")

    def filter_queryset(self, request, queryset, view):
        if not 'bbox' in request.query_params:
            return queryset

        try:
            bbox = json.loads(request.query_params['bbox'])
        except json.JSONDecodeError:
            raise ValidationError(self.error_message)

        if not len(bbox) == 4:
            raise ValidationError(self.error_message)

        try:
            bbox = [float(c) for c in bbox]
        except ValueError:
            raise ValidationError(self.error_message)

        if not (-180. <= bbox[0] < bbox[2] <= 180.) or not (-90. <= bbox[1] < bbox[3] <= 90):
            raise ValidationError(self.error_message)

        bbox = Polygon.from_bbox(bbox)

        return queryset.filter(coordinates__intersects=bbox)


class EventFilterSet(django_filters.rest_framework.FilterSet):
    subtype = django_filters.ModelChoiceFilter(
        name='subtype', to_field_name='label', queryset=EventSubtype.objects.all()
    )
    class Meta:
        model = Event
        fields = ('subtype', )


class EventsView(ListAPIView):
    serializer_class = serializers.MapEventSerializer
    filter_backends = (BBoxFilterBackend, DjangoFilterBackend, )
    filter_class = EventFilterSet
    authentication_classes = []

    def get_queryset(self):
        return Event.objects.upcoming().filter(coordinates__isnull=False).select_related('subtype')

    @cache.cache_control(max_age=300, public=True)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class GroupFilterSet(django_filters.rest_framework.FilterSet):
    subtype = django_filters.ModelChoiceFilter(
        name='subtypes', to_field_name='label', queryset=SupportGroupSubtype.objects.all()
    )
    class Meta:
        model = SupportGroup
        fields = ('subtype', )


class GroupsView(ListAPIView):
    serializer_class = serializers.MapGroupSerializer
    filter_backends = (BBoxFilterBackend, DjangoFilterBackend, )
    filter_class = GroupFilterSet
    queryset = SupportGroup.objects.active().filter(coordinates__isnull=False).prefetch_related('subtypes')
    authentication_classes = []

    @cache.cache_control(max_age=300, public=True)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


def get_subtype_information(subtype):
    res = {
        'id': subtype.id,
        'label': subtype.label,
        'description': subtype.description,
        'type': subtype.type,
        'hideLabel': subtype.hide_text_label
    }

    if subtype.icon:
        res['iconUrl'] = subtype.icon.url
        if subtype.icon_anchor_x is not None and subtype.icon_anchor_y is not None:
            res['iconAnchor'] = [subtype.icon_anchor_x, subtype.icon_anchor_y]
        else:
            res['iconAnchor'] = [subtype.icon.width // 2, subtype.icon.height // 2]

        if subtype.popup_anchor_y is not None:
            res['popupAnchor'] = -subtype.popup_anchor_y
        else:
            res['popupAnchor'] = -res['iconAnchor'][1]
    elif subtype.icon_name:
        res['iconName'] = subtype.icon_name
        res['color'] = subtype.color

    return res


def get_event_type_information(type, label):
    params = {
        "G": ["#4a64ac", "comments"],
        "M": ["#e14b35", "bullhorn"],
        "A": ["#c2306c", "exclamation"],
        "O": ["#49b37d", "calendar"]
    }

    return {
        'id': type,
        'label': label,
        'color': params[type][0],
        'iconName': params[type][1],
    }


def get_group_type_information(type, label):
    params = {
        "L": ['#4a64ac', 'users'],
        "B": ['#49b37d', 'book'],
        "F": ['#e14b35', 'cog'],
        "P": ['#f4981e', 'industry'],
    }

    return {
        'id': type,
        'label': label,
        'color': params[type][0],
        'iconName': params[type][1],
    }


class EventMapView(TemplateView):
    template_name = 'carte/events.html'

    @xframe_options_exempt
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        subtypes = EventSubtype.objects.all()

        params = QueryDict(mutable=True)

        if 'subtype' in self.request.GET:
            subtype_label = self.request.GET['subtype']
            subtypes = subtypes.filter(label=subtype_label)
            params['subtype'] = self.request.GET['subtype']

        subtype_info = [get_subtype_information(st) for st in subtypes]
        types = {s.type for s in subtypes}
        type_info = [get_event_type_information(id, str(label)) for id, label in EventSubtype.TYPE_CHOICES if id in types]

        querystring = ('?' + params.urlencode()) if params else ''

        return super().get_context_data(
            type_config=mark_safe(json.dumps(type_info)),
            subtype_config=mark_safe(json.dumps(subtype_info)),
            querystring=querystring,
            **kwargs
        )


class SingleEventMapView(DetailView):
    template_name = 'carte/single_event.html'
    queryset = Event.objects.published()

    @xframe_options_exempt
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        subtype = self.object.subtype
        type_info = get_event_type_information(subtype.type, subtype.get_type_display())
        subtype_info = get_subtype_information(subtype)

        if 'iconUrl' in subtype_info or 'iconName' in subtype_info:
            icon_config = subtype_info
        else:
            icon_config = type_info

        return super().get_context_data(
            subtype_config=mark_safe(json.dumps(icon_config)),
            coordinates=mark_safe(json.dumps(self.object.coordinates.coords)),
            **kwargs
        )


class GroupMapView(TemplateView):
    template_name = 'carte/groups.html'

    @xframe_options_exempt
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        subtypes = SupportGroupSubtype.objects.all()

        params = QueryDict(mutable=True)

        subtype_label = self.request.GET.get('subtype', None)

        if subtype_label is not None:
            subtypes = subtypes.filter(label=subtype_label)
            params['subtype'] = self.request.GET['subtype']

        subtype_info = [get_subtype_information(st) for st in subtypes]
        types = {s.type for s in subtypes}
        type_info = [get_group_type_information(id, str(label)) for id, label in SupportGroup.TYPE_CHOICES if subtype_label is None or id in types]

        querystring = ('?' + params.urlencode()) if params else ''

        return super().get_context_data(
            type_config=mark_safe(json.dumps(type_info)),
            subtype_config=mark_safe(json.dumps(subtype_info)),
            querystring=querystring,
            **kwargs
        )


class SingleGroupMapView(DetailView):
    template_name = 'carte/single_group.html'
    queryset = SupportGroup.objects.active().all()
    context_object_name = 'group'

    @xframe_options_exempt
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        type_info = get_group_type_information(self.object.type, self.object.get_type_display())
        subtype = self.object.subtypes.first()
        subtype_info = subtype and get_subtype_information(subtype)

        if subtype_info and ('iconUrl' in subtype_info or 'iconName' in subtype_info):
            icon_config = subtype_info
        else:
            icon_config = type_info

        return super().get_context_data(
            subtype_config=mark_safe(json.dumps(icon_config)),
            coordinates=mark_safe(json.dumps(self.object.coordinates.coords)),
            **kwargs
        )
