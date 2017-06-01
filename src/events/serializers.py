from rest_framework import serializers, exceptions
from django.utils.translation import ugettext as _
from lib.serializers import (
    LegacyBaseAPISerializer, LegacyLocationAndContactMixin, RelatedLabelField, UpdatableListSerializer
)

from people.models import Person

from . import models


class LegacyEventSerializer(LegacyBaseAPISerializer, LegacyLocationAndContactMixin, serializers.HyperlinkedModelSerializer):
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
            'url': {'view_name': 'legacy:event-detail'},
        }


class CalendarSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Calendar
        fields = ('url', 'id', 'label', 'description')
        extra_kwargs = {
            'url': {'view_name': 'legacy:calendar-detail'},
        }


class EventTagSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.EventTag
        fields = ('url', 'id', 'label', 'description')
        extra_kwargs = {
            'url': {'view_name': 'legacy:eventtag-detail'},
        }


class EventRSVPListSerializer(UpdatableListSerializer):
    matching_attr = 'person'

    def get_additional_fields(self):
        return {
            'event_id': self.context['event']
        }


class RSVPSerializer(serializers.HyperlinkedModelSerializer):
    """Basic RSVPSerializer used to show and edit existing RSVPs
    
    This serializer does not allow changing the person or event. Instead, this RSVP should be canceled and another
    one created.
    """
    class Meta:
        model = models.RSVP
        fields = ('id', 'url', 'person', 'event', 'guests', 'canceled', )
        read_only_fields = ('id', 'url', 'person', 'event', )
        extra_kwargs = {
            'url': {'view_name': 'legacy:rsvp-detail'},
            'person': {'view_name': 'legacy:person-detail'},
            'event': {'view_name': 'legacy:event-detail'},
        }


class RSVPCreationSerializer(serializers.HyperlinkedModelSerializer):
    """Basic RSVPSerializer used to create RSVPS
    
    Unlike the basic RSVPSerializer, it allows the user to set the ̀person` and `event` fields.
    """
    class Meta:
        fields = ('person', 'event', 'guests', 'canceled')
        read_only_fields = ()
        extra_kwargs = {
            'url': {'view_name': 'legacy:rsvp-detail'},
            'person': {'view_name': 'legacy:person-detail', 'read_only': False, 'queryset': Person.objects.all()},
            'event': {'view_name': 'legacy:event-detail', 'read_only': False, 'queryset': models.Event.objects.all()},
        }


class EventRSVPBulkSerializer(serializers.HyperlinkedModelSerializer):
    """RSVPSerializer for bulk updating of an event's RSVPs
    
    There is no event field (the event is transmitted as part of the route).
    """
    class Meta:
        list_serializer_class = EventRSVPListSerializer
        model = models.RSVP
        fields = ('person', 'guests', 'canceled', )
        extra_kwargs = {
            'person': {'view_name': 'legacy:person-detail', 'read_only': False, 'queryset': Person.objects.all()},
        }


class EventRSVPCreatableSerializer(serializers.HyperlinkedModelSerializer):
    """RSVPSerializer used to create 
    
    """
    class Meta:
        model = models.RSVP
        fields = ('person', 'guests', 'canceled', )
        extra_kwargs = {
            'person': {'view_name': 'legacy:person-detail', 'read_only': False, 'queryset': Person.objects.all()},
        }

    def validate_person(self, value):
        event_id = self.context['event']
        if models.RSVP.objects.filter(event_id=event_id, person_id=value).exists():
            raise exceptions.ValidationError(_('Un RSVP existe déjà pour ce couple événement/personne'), code='unique_rsvp')

        return value

    def validate(self, attrs):
        attrs['event_id'] = self.context['event']

        return attrs
