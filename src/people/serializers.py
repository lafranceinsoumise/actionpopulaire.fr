from django.db import transaction
from django.db.utils import IntegrityError
from rest_framework import serializers

from lib.serializers import (
    LegacyBaseAPISerializer, LegacyLocationMixin, RelatedLabelField, UpdatableListSerializer
)
from clients.serializers import PersonAuthorizationSerializer

from . import models


class PersonEmailListSerializer(UpdatableListSerializer):
    matching_attr = 'address'

    def get_additional_fields(self):
        return {
            'person_id': self.context['person']
        }


class PersonEmailSerializer(serializers.ModelSerializer):
    """Basic PersonEmail serializer used to show and edit existing Memberships

    This serializer does not allow changing the email address. Instead, this email should be deleted and
    another one created.
    """

    class Meta:
        model = models.PersonEmail
        list_serializer_class = PersonEmailListSerializer
        fields = ('address', 'bounced', 'bounced_date', )


class LegacyPersonSerializer(LegacyLocationMixin, LegacyBaseAPISerializer):
    tags = RelatedLabelField(
        many=True,
        required=False,
        queryset=models.PersonTag.objects.all()
    )

    email_opt_in = serializers.BooleanField(
        source='subscribed',
        required=False,
    )

    email = serializers.EmailField(
        required=True
    )

    emails = PersonEmailSerializer(many=True, required=False)

    rsvps = serializers.HyperlinkedRelatedField(
        view_name='legacy:rsvp-detail',
        read_only=True,
        many=True
    )

    groups = serializers.PrimaryKeyRelatedField(
        read_only=True,
        many=True,
        source='supportgroups'
    )

    memberships = serializers.HyperlinkedRelatedField(
        view_name='legacy:membership-detail',
        read_only=True,
        many=True
    )

    authorizations = PersonAuthorizationSerializer(
        many=True,
        read_only=True
    )

    def update(self, instance, validated_data):
        emails = validated_data.pop('emails', None)
        email = validated_data.pop('email', None)
        with transaction.atomic():
            super().update(instance, validated_data)
            if emails is not None:
                for item in emails:
                    instance.add_email(item['address'])

            if email is not None:
                if emails is None or email not in [item['address'] for item in emails]:
                    instance.add_email(email)
                instance.set_primary_email(email)

        return instance

    class Meta:
        model = models.Person
        fields = (
            'url', '_id', 'id', 'email', 'emails', 'first_name', 'last_name', 'bounced', 'bounced_date',
            '_created', '_updated', 'email_opt_in', 'events', 'rsvps', 'groups', 'memberships', 'tags',
            'location', 'authorizations',
        )
        read_only_fields = ('url', '_id', '_created', '_updated')
        extra_kwargs = {
            'url': {'view_name': 'legacy:person-detail',}
        }


class LegacyUnprivilegedPersonSerializer(LegacyPersonSerializer):
    class Meta:
        model = models.Person
        fields = ('url', '_id', 'email', 'first_name', 'last_name', 'email_opt_in',
        'events', 'groups', 'location')
        read_only_fields = ('url', '_id')
        extra_kwargs = {
            'url': {'view_name': 'legacy:person-detail', }
        }


class PersonTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PersonTag
        fields = ('url', 'id', 'label', 'description')
