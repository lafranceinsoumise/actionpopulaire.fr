from django.utils.translation import ugettext as _
from rest_framework import serializers, exceptions

from front.utils import front_url
from lib.serializers import (
    LegacyBaseAPISerializer, LegacyLocationAndContactMixin, RelatedLabelField, UpdatableListSerializer,
    ExistingRelatedLabelField)

from people.models import Person

from . import models


class LegacySupportGroupSerializer(LegacyBaseAPISerializer, LegacyLocationAndContactMixin,
                                   serializers.HyperlinkedModelSerializer):
    path = serializers.SerializerMethodField()
    tags = RelatedLabelField(queryset=models.SupportGroupTag.objects.all(), many=True, required=False)
    subtypes = ExistingRelatedLabelField(queryset=models.SupportGroupSubtype.objects.all(), many=True, required=False)

    def get_path(self, obj):
        return front_url('view_group', absolute=False, args=[obj.id])


    class Meta:
        model = models.SupportGroup
        fields = (
            'url', '_id', 'id', 'name', 'type', 'subtypes', 'description', 'path', 'contact', 'location', 'tags', 'coordinates', 'published'
        )
        extra_kwargs = {
            'url': {'view_name': 'legacy:supportgroup-detail'}
        }


class SummaryGroupSerializer(serializers.ModelSerializer):
    """Serializer used to generate the full list of groups (for the map for instance)
    """
    tags = RelatedLabelField(queryset=models.SupportGroupTag.objects.all(), many=True, required=False)
    subtypes = RelatedLabelField(queryset=models.SupportGroupSubtype.objects.all(), many=True, required=False)

    class Meta:
        model = models.SupportGroup
        fields = ('id', 'name', 'coordinates', 'tags', 'subtypes')


class SupportGroupTagSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.SupportGroupTag
        fields = ('url', 'id', 'label', 'description')


class GroupMembershipListSerializer(UpdatableListSerializer):
    matching_attr = 'person'

    def get_additional_fields(self):
        return {
            'supportgroup_id': self.context['supportgroup']
        }


class MembershipSerializer(serializers.HyperlinkedModelSerializer):
    """Basic Membership serializer used to show and edit existing Memberships

    This serializer does not allow changing the person or support group. Instead, this membership should be deleted and
    another one created.
    """

    class Meta:
        model = models.Membership
        fields = ('id', 'url', 'person', 'supportgroup', 'is_referent', 'is_manager',)
        read_only_fields = ('id', 'url', 'person', 'supportgroup', )
        extra_kwargs = {
            'url': {'view_name': 'legacy:membership-detail'},
            'person': {'view_name': 'legacy:person-detail'},
            'supportgroup': {'view_name': 'legacy:supportgroup-detail'},
        }


class MembershipCreationSerializer(serializers.HyperlinkedModelSerializer):
    """Basic Membership serializer used to create Membership

    Unlike the basic MembershipSerializer, it allows the user to set the ̀person` and `event` fields.
    """

    class Meta:
        fields = ('person', 'supportgroup', 'is_referent', 'is_manager')
        extra_kwargs = {
            'url': {'view_name': 'legacy:rsvp-detail'},
            'person': {'view_name': 'legacy:person-detail', 'read_only': False, 'queryset': Person.objects.all()},
            'supportgroup': {'view_name': 'legacy:supportgroup-detail', 'read_only': False, 'queryset': models.SupportGroup.objects.all()},
        }


class GroupMembershipBulkSerializer(serializers.HyperlinkedModelSerializer):
    """Membership serializer used to update Memberships in bulk for a specific group

    Unlike the basic MembershipSerializer, it allows the user to set the ̀person` field. There is no `event` field, as
    it is set from the URL.
    """

    class Meta:
        model = models.Membership
        list_serializer_class = GroupMembershipListSerializer
        fields = ('person', 'is_referent', 'is_manager')
        extra_kwargs = {
            'person': {'view_name': 'legacy:person-detail', 'read_only': False, 'queryset': Person.objects.all()},
        }


class GroupMembershipCreatableSerializer(serializers.HyperlinkedModelSerializer):
    """Membership serializer used to create new memberships for a given support group.

    """

    class Meta:
        model = models.Membership
        fields = ('person', 'is_referent', 'is_manager')
        extra_kwargs = {
            'person': {'view_name': 'legacy:person-detail', 'read_only': False, 'queryset': Person.objects.all()}
        }

    def validate_person(self, value):
        supportgroup_id = self.context['supportgroup']
        if models.Membership.objects.filter(supportgroup_id=supportgroup_id, person_id=value).exists():
            raise exceptions.ValidationError(_('Un RSVP existe déjà pour ce couple événement/personne'),
                                             code='unique_rsvp')

        return value

    def validate(self, attrs):
        attrs['supportgroup_id'] = self.context['supportgroup']

        return attrs


class SupportGroupSubtypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SupportGroupSubtype
        fields = ('label', 'description', 'color', 'icon', 'type')