import json
from json.decoder import JSONDecodeError
import django_filters
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance


class LegacyDistanceField(forms.Field):
    default_error_messages = {
        'invalid_json': _('Saississez un object JSON valide'),
        'invalid_fields': _("L'objet doit contenir les champs 'maxDistance' et 'coordinates'"),
        'invalid_max_distance': _("'maxDistance' doit être de type numérique"),
        'invalid_coordinates': _("'coordinates' doit être un tableau de coordonnées géographiques [Longitude, Latitude]")
    }

    def to_python(self, value):
        if value in self.empty_values:
            return None

        try:
            obj = json.loads(value)
        except JSONDecodeError:
            raise ValidationError(self.default_error_messages['invalid_json'], code='invalid_json')

        if set(obj) != {'maxDistance', 'coordinates'}:
            raise ValidationError(self.default_error_messages['invalid_fields'], code='invalid_fields')

        try:
            max_distance = float(obj['maxDistance'])
        except ValueError:
            raise ValidationError(self.default_error_messages['invalid_max_distance'], code='invalid_max_distance')

        if not isinstance(obj['coordinates'], list) or len(obj['coordinates']) != 2:
            raise ValidationError(self.default_error_messages['invalid_coordinates'], code='invalid_coordinates')

        try:
            coordinates = [float(c) for c in obj['coordinates']]
        except ValueError:
            raise ValidationError(self.default_error_messages['invalid_coordinates'], code='invalid_coordinates')

        if not (-180. <= coordinates[0] <= 180.) or not (-90. <= coordinates[1] <= 90.):
            raise ValidationError(self.default_error_messages['invalid_coordinates'], code='invalid_coordinates')

        return Point(*coordinates), Distance(m=max_distance)


class LegacyDistanceFilter(django_filters.Filter):
    field_class = LegacyDistanceField
