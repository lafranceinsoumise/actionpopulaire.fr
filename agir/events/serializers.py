from rest_framework import serializers

from . import models


class EventSubtypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EventSubtype
        fields = ("label", "description", "color", "icon", "type")
