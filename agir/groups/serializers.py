from django_countries.serializers import CountryFieldMixin
from rest_framework import serializers

from . import models
from .models import Membership
from ..front.serializer_utils import RoutesField


class SupportGroupSerializer(CountryFieldMixin, serializers.ModelSerializer):
    class Meta:
        model = models.SupportGroup
        fields = (
            "id",
            "name",
            "type",
            "subtypes",
            "contact_name",
            "contact_email",
            "location_address1",
            "location_address2",
            "location_zip",
            "location_city",
            "location_country",
            "coordinates",
        )


GROUP_ROUTES = {
    "page": "view_group",
    "map": "carte:single_group_map",
    "calendar": "ics_group",
    "manage": "manage_group",
    "edit": "edit_group",
    "quit": "quit_group",
}


class SupportGroupSubtypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SupportGroupSubtype
        fields = ("label", "description", "color", "icon", "type")


class SupportGroupReactSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    description = serializers.CharField()
    type = serializers.CharField()
    typeLabel = serializers.SerializerMethodField()

    url = serializers.HyperlinkedIdentityField(view_name="view_group")

    eventCount = serializers.ReadOnlyField(source="events_count")
    membersCount = serializers.SerializerMethodField(source="members_count")
    isMember = serializers.SerializerMethodField()
    isManager = serializers.SerializerMethodField()
    labels = serializers.SerializerMethodField()

    routes = RoutesField(routes=GROUP_ROUTES)

    def to_representation(self, instance):
        user = self.context["request"].user
        self.membership = None
        if not user.is_anonymous and user.person:
            self.membership = Membership.objects.filter(
                person=user.person, supportgroup=instance
            ).first()
        return super().to_representation(instance)

    def get_membersCount(self, obj):
        return obj.members_count

    def get_isMember(self, obj):
        return self.membership is not None

    def get_isManager(self, obj):
        return (
            self.membership is not None
            and self.membership.membership_type >= Membership.MEMBERSHIP_TYPE_MANAGER
        )

    def get_typeLabel(self, obj):
        return obj.get_type_display()

    def get_labels(self, obj):
        return [
            s.description
            for s in obj.subtypes.all()
            if s.description and not s.hide_text_label
        ]
