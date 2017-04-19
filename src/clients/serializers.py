from rest_framework import serializers

from . import models

from lib.serializers import RelatedLabelField, LegacyBaseAPISerializer


class AuthorizationSerializer(serializers.ModelSerializer):
    scopes = RelatedLabelField(queryset=models.Scope.objects.all())

    class Meta:
        model = models.Authorization
        fields = ('url', 'id', 'person', 'client', 'scopes')


class LegacyClientSerializer(LegacyBaseAPISerializer):
    id = serializers.CharField(
        read_only=True,
        source='label'
    )

    class Meta:
        model = models.Client
        fields = ('_id', 'id', 'url', 'name', 'scopes', 'uris', 'trusted')
