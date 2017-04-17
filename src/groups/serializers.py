from rest_framework import serializers
from lib.serializers import LegacyBaseAPISerializer, LegacyLocationAndContactMixin, RelatedLabelField

from . import models


class LegacySupportGroupSerializer(LegacyBaseAPISerializer, LegacyLocationAndContactMixin, serializers.HyperlinkedModelSerializer):
    tags = RelatedLabelField(queryset=models.SupportGroupTag.objects.all(), many=True)

    class Meta:
        model = models.SupportGroup
        fields = (
            'url', '_id', 'id', 'name', 'description', 'nb_path', 'contact', 'location', 'tags'
        )
        extra_kwargs = {
            'url': {'view_name': 'legacy:supportgroup-detail'}
        }


class SupportGroupTagSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.SupportGroupTag
        fields = ('url', 'id', 'label', 'description')
