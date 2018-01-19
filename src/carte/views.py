import json
from django.contrib.gis.geos import Polygon
from django.utils.translation import ugettext as _
from django.utils.html import mark_safe
from django.views.generic import TemplateView, DetailView
from django.contrib.staticfiles.templatetags.staticfiles import static
from rest_framework.generics import ListAPIView
from rest_framework.exceptions import ValidationError

from events.models import Event, EventSubtype
from groups.models import SupportGroup

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


class ZonedView(ListAPIView):
    filter_backends = (BBoxFilterBackend,)


class EventsView(ZonedView):
    serializer_class = serializers.MapEventSerializer
    filter_backends = (BBoxFilterBackend,)

    def get_queryset(self):
        return Event.objects.upcoming()


class GroupsView(ZonedView):
    serializer_class = serializers.MapGroupSerializer
    queryset = SupportGroup.active.all()


def get_subtype_information(subtype):
    res = {
        'id': subtype.id,
        'label': subtype.label,
        'color': subtype.color,
        'type': subtype.type,
    }

    if subtype.icon:
        res['iconUrl'] = subtype.icon.url
        if subtype.icon_anchor_x is not None and subtype.icon_anchor_y is not None:
            res['iconAnchor'] = [subtype.icon_anchor_x, subtype.icon_anchor_y]
        else:
            res['iconAnchor'] = [subtype.icon.width / 2, subtype.icon.height / 2]

        if subtype.popup_anchor_x is not None and subtype.popup_anchor_y is not None:
            res['iconAnchor'] = [subtype.popup_anchor_x, subtype.popup_anchor_y]
        else:
            res['iconAnchor'] = [subtype.icon.width / 2, 0]

    else:
        res['iconUrl'] = static('carte/marker-icon.png')
        res['iconAnchor'] = [12, 41]
        res['popupAnchor'] = [0, -41]

    return res
