from rest_framework import serializers

from events.models import Event, EventSubtype
from groups.models import SupportGroup


class MapEventSerializer(serializers.ModelSerializer):
    subtype = serializers.PrimaryKeyRelatedField(queryset=EventSubtype.objects.all())

    class Meta:
        model = Event
        fields = ('id', 'name', 'coordinates', 'start_time', 'end_time', 'tags', 'subtype')


class MapGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportGroup
        fields = ('id', 'name', 'coordinates', 'tags')
