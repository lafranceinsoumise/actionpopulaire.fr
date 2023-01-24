from django_countries.serializer_fields import CountryField
from rest_framework import serializers, fields

from agir.event_requests import models


class EventThemeSerializer(serializers.ModelSerializer):
    type = fields.CharField(source="event_theme_type.name", read_only=True)

    class Meta:
        model = models.EventTheme
        fields = ("id", "name", "type")


class EventRequestSerializer(serializers.ModelSerializer):
    status = fields.CharField(source="get_status_display", read_only=True)
    theme = EventThemeSerializer(source="event_theme", read_only=True)
    zip = serializers.CharField(source="location_zip", read_only=True)
    city = serializers.CharField(source="location_city", read_only=True)
    country = CountryField(source="location_country", read_only=True)

    class Meta:
        model = models.EventRequest
        fields = ("id", "status", "theme", "datetimes", "zip", "city", "country")


class EventSpeakerRequestSerialier(serializers.ModelSerializer):
    is_answerable = fields.BooleanField(read_only=True)
    event_request = EventRequestSerializer(read_only=True)

    class Meta:
        model = models.EventSpeakerRequest
        fields = (
            "id",
            "is_answerable",
            "event_request",
            "available",
            "accepted",
            "datetime",
            "comment",
        )


class EventSpeakerSerializer(serializers.ModelSerializer):
    event_requests = EventRequestSerializer(many=True, read_only=True)
    event_speaker_requests = EventSpeakerRequestSerialier(many=True, read_only=True)
    event_themes = EventThemeSerializer(many=True, read_only=True)

    class Meta:
        model = models.EventSpeaker
        fields = "__all__"
