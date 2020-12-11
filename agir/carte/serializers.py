from django_countries.serializers import CountryFieldMixin
from rest_framework import serializers

from ..events.models import Event
from ..groups.models import SupportGroup


class MapEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ("id", "name", "coordinates", "start_time", "end_time", "subtype")


class MapGroupSerializer(CountryFieldMixin, serializers.ModelSerializer):
    subtype = serializers.SerializerMethodField("get_first_subtype")
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = SupportGroup
        fields = (
            "id",
            "name",
            "coordinates",
            "type",
            "subtype",
            "subtypes",
            "is_active",
            "location_country",
        )

    def get_first_subtype(self, obj):
        return obj.subtypes.all()[0].id if obj.subtypes.all() else None
