from rest_framework import serializers

from . import models
from ..lib.serializers import ExistingRelatedLabelField


class EventSerializer(serializers.ModelSerializer):
    subtype = ExistingRelatedLabelField(
        queryset=models.EventSubtype.objects.all(), required=False
    )

    class Meta:
        model = models.Event
        fields = (
            "id",
            "name",
            "description",
            "start_time",
            "end_time",
            "contact_name",
            "contact_email",
            "location_address1",
            "location_address2",
            "location_city",
            "location_zip",
            "location_country",
            "coordinates",
            "subtype",
        )


class EventSubtypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EventSubtype
        fields = ("label", "description", "color", "icon", "type")
