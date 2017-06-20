import json
from json.decoder import JSONDecodeError
import django_filters
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django.contrib.gis.db.models.functions import Distance as DistanceFunction
from rest_framework.exceptions import ValidationError as DRFValidationError


def check_coordinates(coordinates):
    if not isinstance(coordinates, list) or len(coordinates) != 2:
        return False

    if not isinstance(coordinates[0], float) or not isinstance(coordinates[1], float):
        return False

    if not (-180. <= coordinates[0] <= 180.) or not (-90. <= coordinates[1] <= 90.):
        return False

    return True


class LegacyDistanceField(forms.Field):
    default_error_messages = {
        'invalid_json': _('Saississez un object JSON valide'),
        'invalid_fields': _("L'objet doit contenir les champs 'maxDistance' et 'coordinates'"),
        'invalid_max_distance': _("'maxDistance' doit être de type numérique"),
        'invalid_coordinates': _(
            "'coordinates' doit être un tableau de coordonnées géographiques [Longitude, Latitude]")
    }

    def to_python(self, value):
        if value in self.empty_values:
            return None

        try:
            obj = json.loads(value)
        except JSONDecodeError:
            raise DRFValidationError(self.default_error_messages['invalid_json'], code='invalid_json')

        if set(obj) != {'maxDistance', 'coordinates'}:
            raise DRFValidationError(self.default_error_messages['invalid_fields'], code='invalid_fields')

        max_distance = obj['maxDistance']
        coordinates = obj['coordinates']

        if not isinstance(max_distance, float):
            raise DRFValidationError(self.default_error_messages['invalid_max_distance'], code='invalid_max_distance')

        if not check_coordinates(coordinates):
            raise DRFValidationError(self.default_error_messages['invalid_coordinates'], code='invalid_coordinates')

        return Point(*coordinates), Distance(m=max_distance)


class DistanceFilter(django_filters.Filter):
    field_class = LegacyDistanceField


class OrderByDistanceToBackend(object):
    error_message = _("le paramètre 'order_by_distance_to' devrait être un tableau JSON [lon, lat]")

    def filter_queryset(self, request, queryset, view):
        if not 'order_by_distance_to' in request.query_params:
            return queryset

        try:
            coordinates = json.loads(request.query_params['order_by_distance_to'])
        except JSONDecodeError:
            raise DRFValidationError(detail=self.error_message)


        if not check_coordinates(coordinates):
            raise DRFValidationError(detail=self.error_message)

        return queryset.annotate(distance=DistanceFunction('coordinates', Point(coordinates, srid=4326))).order_by('distance')
