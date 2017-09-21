from django.utils.translation import ugettext as _
from rest_framework import serializers, exceptions

from authentication.models import Role
from . import models

from lib.serializers import RelatedLabelField, LegacyBaseAPISerializer, UpdatableListSerializer


class AuthorizationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Authorization
        fields = ('url', 'person', 'client', 'scopes')
        extra_kwargs = {
            'url': {'view_name': 'legacy:authorization-detail'},
            'person': {'view_name': 'legacy:person-detail'},
            'client': {'view_name': 'legacy:client-detail'}
        }


class ScopeSerializer(serializers.Serializer):
    name = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)


class LegacyClientSerializer(LegacyBaseAPISerializer):
    id = serializers.CharField(
        read_only=True,
        source='label'
    )

    class Meta:
        model = models.Client
        fields = ('_id', 'id', 'url', 'name', 'description', 'scopes', 'uris', 'trusted')
        read_only_fields = ('_id', 'id', 'url')
        extra_kwargs = {
            'url': {'view_name': 'legacy:client-detail',}
        }


class ClientAuthenticationSerializer(serializers.Serializer):
    id = serializers.CharField(
        max_length=40,
        required=True,
    )

    secret = serializers.CharField(
        max_length=250,
        required=True,
    )

    def validate(self, attrs):
        id = attrs['id']
        secret = attrs['secret']

        try:
            client = models.Client.objects.select_related('role').get(label=id)

            if client.role.check_password(secret) and client.oauth_enabled:
                return {"client": client}

        except models.Client.DoesNotExist:
            # avoid timing attacks by doing a hash round
            Role().set_password(secret)

        raise exceptions.ValidationError(_("Authentification incorrecte"))


class PersonAuthorizationSerializer(serializers.HyperlinkedModelSerializer):
    scopes = serializers.SlugRelatedField(
        read_only=True,
        slug_field='label',
        many=True
    )

    class Meta:
        model = models.Authorization
        fields = ('url', 'client', 'scopes')
        extra_kwargs = {
            'url': {'view_name': 'legacy:authorization-detail'},
            'client': {'view_name': 'legacy:client-detail',}
        }
