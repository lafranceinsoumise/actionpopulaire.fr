import json
from json.decoder import JSONDecodeError
import django_filters
from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django.contrib.gis.db.models.functions import Distance as DistanceFunction
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError


def check_coordinates(coordinates):
    if not isinstance(coordinates, list) or len(coordinates) != 2:
        return False

    try:
        for i, val in enumerate(coordinates):
            coordinates[i] = float(val)
    except ValueError:
        return False

    if not (-180.0 <= coordinates[0] <= 180.0) or not (-90.0 <= coordinates[1] <= 90.0):
        return False

    return True


class LegacyDistanceField(forms.Field):
    default_error_messages = {
        "invalid_json": _("Saississez un object JSON valide"),
        "invalid_fields": _(
            "L'objet doit contenir les champs 'max_distance' et 'coordinates'"
        ),
        "invalid_max_distance": _("'max_distance' doit être de type numérique"),
        "invalid_coordinates": _(
            "'coordinates' doit être un tableau de coordonnées géographiques [Longitude, Latitude]"
        ),
    }

    def to_python(self, value):
        if value in self.empty_values:
            return None

        try:
            obj = json.loads(value)
        except JSONDecodeError:
            raise DjangoValidationError(
                self.default_error_messages["invalid_json"], code="invalid_json"
            )

        if set(obj) != {"max_distance", "coordinates"}:
            raise DjangoValidationError(
                self.default_error_messages["invalid_fields"], code="invalid_fields"
            )

        max_distance = obj["max_distance"]
        coordinates = obj["coordinates"]

        try:
            max_distance = float(max_distance)
        except ValueError:
            raise DjangoValidationError(
                self.default_error_messages["invalid_max_distance"],
                code="invalid_max_distance",
            )

        if not check_coordinates(coordinates):
            raise DjangoValidationError(
                self.default_error_messages["invalid_coordinates"],
                code="invalid_coordinates",
            )

        return Point(*coordinates), Distance(m=max_distance)


class DistanceFilter(django_filters.Filter):
    field_class = LegacyDistanceField


class OrderByDistanceToBackend(object):
    """ """

    error_message = _(
        "le paramètre 'order_by_distance_to' devrait être un tableau JSON [lon, lat]"
    )

    def filter_queryset(self, request, queryset, view):
        if not "order_by_distance_to" in request.query_params:
            return queryset

        try:
            coordinates = json.loads(request.query_params["order_by_distance_to"])
        except JSONDecodeError:
            raise DRFValidationError(detail=self.error_message)

        if not check_coordinates(coordinates):
            raise DRFValidationError(detail=self.error_message)

        return queryset.annotate(
            distance=DistanceFunction("coordinates", Point(coordinates, srid=4326))
        ).order_by("distance")


class FixedModelMultipleChoiceFilter(django_filters.ModelMultipleChoiceFilter):
    def get_filter_predicate(self, v):
        return {self.field_name: v}


class ChoiceInFilter(django_filters.BaseInFilter, django_filters.ChoiceFilter):
    pass


class ModelChoiceInFilter(
    django_filters.BaseInFilter, django_filters.ModelChoiceFilter
):
    pass
