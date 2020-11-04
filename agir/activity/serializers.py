from rest_framework import serializers

from agir.events.serializers import EventSerializer
from agir.groups.serializers import SupportGroupSerializer
from agir.lib.serializers import FlexibleFieldsMixin
from agir.people.serializers import PersonSerializer


class ActivitySerializer(FlexibleFieldsMixin, serializers.Serializer):
    id = serializers.CharField()
    type = serializers.CharField()
    subtype = serializers.CharField(source="type")

    timestamp = serializers.DateTimeField()

    event = EventSerializer(
        fields=[
            "id",
            "name",
            "startTime",
            "endTime",
            "participantCount",
            "illustration",
            "schedule",
            "location",
            "rsvp",
            "routes",
        ]
    )
    supportGroup = SupportGroupSerializer(source="supportgroup", fields=["name", "url"])
    individual = PersonSerializer(fields=["fullName", "email"])

    status = serializers.CharField()
