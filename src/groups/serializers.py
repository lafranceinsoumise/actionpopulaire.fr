from rest_framework import serializers
from lib.serializers import LegacyBaseAPISerializer, LegacyLocationAndContactMixin, RelatedLabelField

from . import models


class LegacySupportGroupSerializer(LegacyBaseAPISerializer, LegacyLocationAndContactMixin, serializers.HyperlinkedModelSerializer):
    path = serializers.CharField(source='nb_path', required=False)
    tags = RelatedLabelField(queryset=models.SupportGroupTag.objects.all(), many=True, required=False)


    class Meta:
        model = models.SupportGroup
        fields = (
            'url', '_id', 'id', 'name', 'description', 'path', 'contact', 'location', 'tags', 'coordinates'
        )
        extra_kwargs = {
            'url': {'view_name': 'legacy:supportgroup-detail'}
        }


class SupportGroupTagSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.SupportGroupTag
        fields = ('url', 'id', 'label', 'description')


class MembershipSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Membership
        fields = ('url', 'person', 'support_group', 'is_referent',)
