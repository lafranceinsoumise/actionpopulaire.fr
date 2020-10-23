from rest_framework import serializers

from agir.events.serializers import EventSerializer
from agir.groups.serializers import SupportGroupSerializer


class ActivitySerializer(serializers.Serializer):
    type = serializers.CharField()

    event = EventSerializer()
    group = SupportGroupSerializer()
