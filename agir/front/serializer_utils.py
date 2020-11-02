from django.conf import settings
from rest_framework import serializers

from agir.lib.utils import front_url


class MediaURLField(serializers.URLField):
    def to_representation(self, value):
        return f"{settings.MEDIA_URL}{value}" if value else None

    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        if value.startswith(settings.MEDIA_URL):
            value = value[len(settings.MEDIA_URL) :]

        return value


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
            key: front_url(view_name, args=(value.pk,))
            for key, view_name in self.routes.items()
        }

        if method is not None:
            routes.update(method(value))

        return routes
