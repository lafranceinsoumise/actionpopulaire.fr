from rest_framework import serializers
from lib.serializers import LegacyBaseAPISerializer

from . import models


class LegacyPersonSerializer(LegacyBaseAPISerializer, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Person
        fields = (
            'url', '_id', 'id', 'email', 'first_name', 'last_name', 'bounced', 'bounced_date', '_created', '_updated'
        )
        extra_kwargs = {
            'url': {'view_name': 'legacy:person-detail',}
        }
