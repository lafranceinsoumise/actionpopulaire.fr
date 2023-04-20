from django_countries.serializers import CountryFieldMixin
from rest_framework import serializers

from ..events.models import Event
from ..groups.models import SupportGroup
from ..lib.utils import front_url


class MapEventSerializer(serializers.ModelSerializer):
    date = serializers.CharField(source="get_simple_display_date", read_only=True)
    link = serializers.SerializerMethodField(read_only=True)

    def get_link(self, obj):
        return front_url("map_event_details", args=(obj.pk,), absolute=True)

    class Meta:
        model = Event
        fields = (
            "id",
            "name",
            "coordinates",
            "date",
            "link",
            "start_time",
            "end_time",
            "subtype",
        )


class MapGroupSerializer(CountryFieldMixin, serializers.ModelSerializer):
    subtype = serializers.SerializerMethodField("get_first_subtype")
    is_active = serializers.BooleanField()
    is_certified = serializers.BooleanField()
    link = serializers.SerializerMethodField()

    def get_link(self, obj):
        return front_url("map_group_details", args=(obj.pk,), absolute=True)

    def get_first_subtype(self, obj):
        return obj.subtypes.active().values_list("id", flat=True).first()

    class Meta:
        model = SupportGroup
        fields = read_only_fields = (
            "id",
            "name",
            "coordinates",
            "type",
            "subtype",
            "subtypes",
            "is_active",
            "is_certified",
            "location_country",
            "link",
        )
