from django.conf import settings
from django_countries.serializers import CountryFieldMixin
from rest_framework import serializers

from . import models
from .actions import get_promo_codes
from .models import Membership
from ..front.serializer_utils import RoutesField
from agir.lib.serializers import (
    FlexibleFieldsMixin,
    LocationSerializer,
    ContactMixinSerializer,
)
from agir.people.serializers import PersonSerializer
from ..lib.utils import front_url, admin_url


class SupportGroupLegacySerializer(CountryFieldMixin, serializers.ModelSerializer):
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
    "membershipTransfer": "transfer_group_members",
}


class SupportGroupSubtypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SupportGroupSubtype
        fields = ("label", "description", "color", "icon", "type")


class SupportGroupSerializer(FlexibleFieldsMixin, serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    description = serializers.CharField(source="html_description")
    type = serializers.CharField()
    typeLabel = serializers.SerializerMethodField()

    url = serializers.HyperlinkedIdentityField(view_name="view_group")

    eventCount = serializers.ReadOnlyField(source="events_count")
    membersCount = serializers.SerializerMethodField(source="members_count")
    isMember = serializers.SerializerMethodField()
    isManager = serializers.SerializerMethodField()
    labels = serializers.SerializerMethodField()

    discountCodes = serializers.SerializerMethodField()
    is2022 = serializers.SerializerMethodField()
    isFull = serializers.SerializerMethodField()

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

    def get_routes(self, obj):
        additional_routes = {}
        if obj.is_certified:
            additional_routes["fund"] = front_url(
                "donation_amount", query={"group": obj.pk}
            )
        return {}

    def get_discountCodes(self, obj):
        if (
            self.membership is not None
            and self.membership.membership_type >= Membership.MEMBERSHIP_TYPE_MANAGER
            and obj.tags.filter(label=settings.PROMO_CODE_TAG).exists()
        ):
            return [
                {"code": code, "expirationDate": date}
                for code, date in get_promo_codes(obj)
            ]
        return []

    def get_is2022(self, obj):
        return obj.is_2022

    def get_isFull(self, obj):
        return obj.is_full


class SupportGroupDetailSerializer(FlexibleFieldsMixin, serializers.Serializer):
    id = serializers.UUIDField()

    isMember = serializers.SerializerMethodField()
    isManager = serializers.SerializerMethodField()

    name = serializers.CharField()
    type = serializers.SerializerMethodField()
    description = serializers.CharField(source="html_description")
    is2022 = serializers.SerializerMethodField()
    isFull = serializers.SerializerMethodField()
    location = LocationSerializer(source="*")
    contact = ContactMixinSerializer(source="*")

    referents = serializers.SerializerMethodField()
    # TODO: add links to SupporGroup model
    links = []

    facts = serializers.SerializerMethodField()
    iconConfiguration = serializers.SerializerMethodField()

    routes = serializers.SerializerMethodField()
    discountCodes = serializers.SerializerMethodField()

    def to_representation(self, instance):
        user = self.context["request"].user
        self.membership = None
        self.user = user
        if not user.is_anonymous and user.person:
            self.membership = Membership.objects.filter(
                person=user.person, supportgroup=instance
            ).first()
        return super().to_representation(instance)

    def get_isMember(self, obj):
        return self.membership is not None

    def get_isManager(self, obj):
        return (
            self.membership is not None
            and self.membership.membership_type >= Membership.MEMBERSHIP_TYPE_MANAGER
        )

    def get_type(self, obj):
        return obj.get_type_display()

    def get_is2022(self, obj):
        return obj.is_2022

    def get_isFull(self, obj):
        return obj.is_full

    def get_referents(self, obj):
        return PersonSerializer(
            obj.referents,
            context=self.context,
            many=True,
            fields=[
                "id",
                "fullName",
                # "avatar",
            ],
        ).data

    def get_facts(self, obj):
        facts = {
            "memberCount": obj.members_count,
            "eventCount": obj.events_count,
            "creationDate": obj.created,
            "isCertified": obj.is_certified,
            # TODO: define what "last activity" means for a group
            "lastActivityDate": None,
        }
        return facts

    def get_iconConfiguration(self, obj):
        if obj.type in models.SupportGroup.TYPE_PARAMETERS:
            configuration = models.SupportGroup.TYPE_PARAMETERS[obj.type]
            return {
                "color": configuration["color"],
                "iconName": configuration["icon_name"],
            }

    def get_routes(self, obj):
        routes = {}
        if obj.is_certified:
            routes["donations"] = front_url("donation_amount", query={"group": obj.pk})
        if self.membership is not None:
            routes["quit"] = front_url("quit_group", kwargs={"pk": obj.pk})
        if (
            self.membership is not None
            and self.membership.membership_type >= Membership.MEMBERSHIP_TYPE_MANAGER
        ):
            routes["createEvent"] = front_url("create_event")
            routes["settings"] = front_url("manage_group", kwargs={"pk": obj.pk})
            routes["edit"] = front_url("edit_group", kwargs={"pk": obj.pk})
            routes["members"] = front_url(
                "manage_group", query={"active": "membership"}, kwargs={"pk": obj.pk}
            )
            routes["animation"] = front_url(
                "manage_group", query={"active": "animation"}, kwargs={"pk": obj.pk}
            )
            routes["membershipTransfer"] = front_url(
                "transfer_group_members", kwargs={"pk": obj.pk}
            )
            if obj.tags.filter(label=settings.PROMO_CODE_TAG).exists():
                routes["materiel"] = front_url(
                    "manage_group", query={"active": "materiel"}, kwargs={"pk": obj.pk}
                )
            if not obj.is_2022:
                routes["invitation"] = front_url(
                    "manage_group",
                    query={"active": "invitation"},
                    kwargs={"pk": obj.pk},
                )
            if obj.is_certified:
                routes["financement"] = front_url(
                    "manage_group",
                    query={"active": "financement"},
                    kwargs={"pk": obj.pk},
                )
        if (
            not self.user.is_anonymous
            and self.user.person
            and self.user.is_staff
            and self.user.has_perm("groups.change_supportgroup")
        ):
            routes["admin"] = admin_url("groups_supportgroup_change", args=[obj.pk])

        return routes

    def get_discountCodes(self, obj):
        if (
            self.membership is not None
            and self.membership.membership_type >= Membership.MEMBERSHIP_TYPE_MANAGER
            and obj.tags.filter(label=settings.PROMO_CODE_TAG).exists()
        ):
            return [
                {"code": code, "expirationDate": date}
                for code, date in get_promo_codes(obj)
            ]
        return []
