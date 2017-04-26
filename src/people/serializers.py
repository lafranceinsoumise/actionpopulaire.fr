from rest_framework import serializers

from lib.serializers import LegacyBaseAPISerializer

from . import models


class LegacyPersonSerializer(LegacyBaseAPISerializer):
    rsvps = serializers.HyperlinkedRelatedField(
        view_name='legacy:rsvp-detail',
        read_only=True,
        many=True
    )
    groups = serializers.PrimaryKeyRelatedField(
        read_only=True,
        many=True,
        source='support_groups'
    )
    memberships = serializers.HyperlinkedRelatedField(
        view_name='legacy:membership-detail',
        read_only=True,
        many=True
    )

    class Meta:
        model = models.Person
        fields = (
            'url', '_id', 'id', 'email', 'first_name', 'last_name', 'bounced', 'bounced_date', '_created', '_updated',
            'events', 'rsvps', 'groups', 'memberships'
        )
        extra_kwargs = {
            'url': {'view_name': 'legacy:person-detail',}
        }


class PersonTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PersonTag
        fields = ('url', 'id', 'label', 'description')
