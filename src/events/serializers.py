from rest_framework import serializers, exceptions
from django.utils.translation import ugettext as _
from lib.serializers import LegacyBaseAPISerializer, LegacyLocationAndContactMixin, RelatedLabelField

from . import models


class LegacyEventSerializer(LegacyBaseAPISerializer, LegacyLocationAndContactMixin, serializers.ModelSerializer):
    calendar = RelatedLabelField(queryset=models.Calendar.objects.all())
    path = serializers.CharField(source='nb_path', required=False)
    tags = RelatedLabelField(queryset=models.EventTag.objects.all(), many=True, required=False)

    class Meta:
        model = models.Event
        fields = (
            'url', '_id', 'id', 'name', 'description', 'path', 'start_time', 'end_time', 'calendar', 'contact',
            'location', 'tags', 'coordinates'
        )
        extra_kwargs = {
            'url': {'view_name': 'legacy:event-detail'}
        }


class CalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Calendar
        fields = ('url', 'id', 'label', 'description')


class EventTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EventTag
        fields = ('url', 'id', 'label', 'description')


class RSVPEventListSerializer(serializers.ListSerializer):
    def update(self, instance, validated_data):

        event_id = self.context['event']
        rsvp_mapping = {rsvp.person_id: rsvp for rsvp in instance}
        try:
            data_mapping = {item['person'].id: item for item in validated_data}
        except KeyError:
            raise exceptions.ValidationError(_('Données invalides en entrée'), code='invalid_data')

        ret = []
        for person_id, data in data_mapping.items():
            rsvp = rsvp_mapping.get(person_id, None)
            data['event_id'] = event_id

            if rsvp is None:
                ret.append(self.child.create(data))
            else:
                ret.append(self.child.update(rsvp, data))

        for person_id, rsvp in rsvp_mapping.items():
            if person_id not in data_mapping:
                rsvp.delete()

        return ret


class RSVPSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RSVP
        fields = ('id', 'url', 'person', 'event', 'guests', )
        read_only_fields = ('id', 'url', 'person', 'event', )
        extra_kwargs = {
            'url': {'view_name': 'legacy:rsvp-detail'}
        }


class RSVPCreationSerializer(RSVPSerializer):
    class Meta(RSVPSerializer.Meta):
        fields = ('person', 'event', 'guests')
        extra_kwargs = {
            'url': {'view_name': 'legacy:rsvp-detail'}
        }


class EventRSVPBulkSerializer(serializers.ModelSerializer):
    class Meta:
        list_serializer_class = RSVPEventListSerializer
        model = models.RSVP
        fields = ('person', 'guests')


class EventRSVPCreatableSerializer(serializers.ModelSerializer):
    class Meta:
        list_serializer_class = RSVPEventListSerializer
        model = models.RSVP
        fields = ('person', 'guests')

    def validate_person(self, value):
        event_id = self.context['event']
        if models.RSVP.objects.filter(event_id=event_id, person_id=value).exists():
            raise exceptions.ValidationError(_('Un RSVP existe déjà pour ce couple événement/personne'), code='unique_rsvp')

        return value

    def validate(self, attrs):
        attrs['event_id'] = self.context['event']

        return attrs
