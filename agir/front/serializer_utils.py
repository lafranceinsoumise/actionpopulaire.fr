from django.conf import settings
from rest_framework import serializers


class MediaURLField(serializers.URLField):
    def to_representation(self, value):
        return f"{settings.MEDIA_URL}{value}" if value else None

    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        if value.startswith(settings.MEDIA_URL):
            value = value[len(settings.MEDIA_URL) :]

        return value
