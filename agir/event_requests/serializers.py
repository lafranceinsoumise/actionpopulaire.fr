import os

from django.template.defaultfilters import filesizeformat
from rest_framework import serializers, fields

from agir.event_requests import models


class EventAssetSerializer(serializers.ModelSerializer):
    size = serializers.SerializerMethodField()
    format = serializers.SerializerMethodField()

    def get_size(self, obj):
        if obj.file:
            return filesizeformat(obj.file.size)

    def get_format(self, obj):
        if obj.file:
            _, extension = os.path.splitext(obj.file.name)
            return extension.replace(".", "").upper()

    class Meta:
        model = models.EventAsset
        fields = read_only_fields = ("id", "name", "file", "size", "format")


class EventThemeSerializer(serializers.ModelSerializer):
    type = fields.CharField(source="event_theme_type.name")

    class Meta:
        model = models.EventTheme
        fields = read_only_fields = ("id", "name", "type")


class EventRequestSerializer(serializers.ModelSerializer):
    status = fields.CharField(source="get_status_display")
    theme = EventThemeSerializer(source="event_theme")
    location = fields.SerializerMethodField()

    def get_location(self, obj):
        return {
            "zip": obj.location_zip,
            "city": obj.location_city,
            "country": obj.location_country.name,
        }

    class Meta:
        model = models.EventRequest
        fields = read_only_fields = (
            "id",
            "status",
            "theme",
            "location",
            "event",
        )


class EventSpeakerRequestSerializer(serializers.ModelSerializer):
    isAnswerable = fields.BooleanField(source="is_answerable")
    eventRequest = fields.UUIDField(source="event_request_id")

    class Meta:
        model = models.EventSpeakerRequest
        fields = (
            "id",
            "isAnswerable",
            "eventRequest",
            "available",
            "accepted",
            "datetime",
            "comment",
        )
        read_only_fields = (
            "id",
            "isAnswerable",
            "eventRequest",
            "accepted",
            "datetime",
        )


class EventSpeakerSerializer(serializers.ModelSerializer):
    themes = EventThemeSerializer(source="event_themes", many=True)
    eventRequests = EventRequestSerializer(source="event_requests.distinct", many=True)
    eventSpeakerRequests = EventSpeakerRequestSerializer(
        source="event_speaker_requests", many=True
    )

    class Meta:
        model = models.EventSpeaker
        fields = (
            "id",
            "available",
            "themes",
            "eventRequests",
            "eventSpeakerRequests",
        )
        read_only_fields = (
            "id",
            "themes",
            "eventRequests",
            "eventSpeakerRequests",
        )
