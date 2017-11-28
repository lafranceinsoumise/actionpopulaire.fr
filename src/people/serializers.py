import uuid
from django.db import transaction
from django.db.utils import IntegrityError
from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from lib.serializers import (
    LegacyBaseAPISerializer, LegacyLocationMixin, RelatedLabelField, UpdatableListSerializer
)
from clients.serializers import PersonAuthorizationSerializer

from . import models


class PersonEmailSerializer(serializers.ModelSerializer):
    """Basic PersonEmail serializer used to show and edit PersonEmail
    """

    def __init__(self, *args, **kwargs):
        serializers.ModelSerializer.__init__(self, *args, **kwargs)
        queryset = models.PersonEmail.objects.all()
        try:
            pk = self.context['view'].kwargs['pk']
        except KeyError:
            pk = None
        if pk is not None:
            try:
                queryset = queryset.exclude(person__id=pk)
            except ValueError:
                queryset = queryset.exclude(person__nb_id=pk)

        self.fields['address'] = serializers.EmailField(
            max_length=254,
            validators=[UniqueValidator(queryset=queryset)])

    bounced = serializers.BooleanField()

    class Meta:
        model = models.PersonEmail
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

    bounced = serializers.BooleanField(
        required=False
    )

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not isinstance(self, LegacyUnprivilegedPersonSerializer):
            self.fields['emails'] = PersonEmailSerializer(required=False, many=True, context=self.context)

    def validate_email(self, value):
        try:
            queryset = models.PersonEmail.objects.all()
            if self.instance is not None:
                queryset = queryset.exclude(person=self.instance)
            queryset.get(address=BaseUserManager.normalize_email(value))
        except models.PersonEmail.DoesNotExist:
            return value

        raise serializers.ValidationError('Email already exists', code='unique')

    def update(self, instance, validated_data):
        emails = validated_data.pop('emails', None)
        email = validated_data.pop('email', None)
        with transaction.atomic():
            super().update(instance, validated_data)
            if emails is not None:
                for item in emails:
                    instance.add_email(item['address'], bounced=item.get('bounced', None), bounced_date=item.get('bounced_date', None))

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
