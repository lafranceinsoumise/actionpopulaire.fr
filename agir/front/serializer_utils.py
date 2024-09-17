import pytz
from pytz.exceptions import UnknownTimeZoneError
from rest_framework import serializers

from agir.lib.utils import front_url


class TimeZoneField(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            pytz.timezone(data)
        except UnknownTimeZoneError:
            raise serializers.ValidationError("TimeZone inconnue")
        return data


class RoutesField(serializers.SerializerMethodField):
    def __init__(self, *, routes=None, **kwargs):
        kwargs.setdefault("source", "*")
        super().__init__(**kwargs)

        if routes is None:
            routes = {}
        self.routes = routes

    def to_representation(self, value):
        method = getattr(self.parent, self.method_name, None)
        routes = {
            key: (
                view_name
                if view_name.startswith("http")
                else front_url(view_name, args=(value.pk,))
            )
            for key, view_name in self.routes.items()
        }

        if method is not None:
            routes.update(method(value))

        return routes
