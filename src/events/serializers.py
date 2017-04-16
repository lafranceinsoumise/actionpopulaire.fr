from rest_framework import serializers
from lib.serializers import LegacyBaseAPISerializer, LegacyLocationAndContactMixin, RelatedLabelField

from . import models


class LegacyEventSerializer(LegacyBaseAPISerializer, LegacyLocationAndContactMixin, serializers.HyperlinkedModelSerializer):
    calendar = RelatedLabelField(queryset=models.Calendar.objects.all())

    class Meta:
        model = models.Event
        fields = (
            'url', '_id', 'id', 'name', 'description', 'nb_path', 'start_time', 'end_time', 'calendar', 'contact',
            'location',
        )
        extra_kwargs = {
            'url': {'view_name': 'legacy:event-detail'}
        }


class CalendarSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Calendar
        fields = ('id', 'label', 'description')
