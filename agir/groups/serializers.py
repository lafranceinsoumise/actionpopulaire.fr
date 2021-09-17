from urllib.parse import urlencode

from django.conf import settings
from django_countries.serializers import CountryFieldMixin
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from agir.groups.tasks import (
    send_support_group_changed_notification,
    geocode_support_group,
)
from agir.lib.geo import get_commune
from agir.lib.serializers import (
    FlexibleFieldsMixin,
    LocationSerializer,
    ContactMixinSerializer,
    NestedContactSerializer,
    NestedLocationSerializer,
)
from agir.people.serializers import PersonSerializer
from . import models
from .actions import get_promo_codes
from .actions.notifications import member_to_follower_notification
from .models import Membership, SupportGroup, SupportGroupExternalLink
from ..front.serializer_utils import RoutesField
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
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(read_only=True)
    description = serializers.CharField(source="html_description", read_only=True)
    type = serializers.CharField(read_only=True)
    typeLabel = serializers.SerializerMethodField(read_only=True)

    url = serializers.HyperlinkedIdentityField(view_name="view_group", read_only=True)

    eventCount = serializers.ReadOnlyField(source="events_count", read_only=True)
    membersCount = serializers.SerializerMethodField(read_only=True)
    isMember = serializers.SerializerMethodField(read_only=True)
    isActiveMember = serializers.SerializerMethodField(read_only=True,)
    isManager = serializers.SerializerMethodField(read_only=True)
    labels = serializers.SerializerMethodField(read_only=True)

    discountCodes = serializers.SerializerMethodField(read_only=True)
    isFull = serializers.SerializerMethodField(read_only=True)

    routes = RoutesField(routes=GROUP_ROUTES, read_only=True)

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

    def get_isActiveMember(self, obj):
        return self.membership is not None and self.membership.is_active_member

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

    def get_isFull(self, obj):
        return obj.is_full


class SupportGroupDetailSerializer(FlexibleFieldsMixin, serializers.Serializer):
    id = serializers.UUIDField(read_only=True,)

    isMember = serializers.SerializerMethodField(read_only=True,)
    isActiveMember = serializers.SerializerMethodField(read_only=True,)
    isManager = serializers.SerializerMethodField(read_only=True,)
    isReferent = serializers.SerializerMethodField(read_only=True,)

    name = serializers.CharField(read_only=True,)
    type = serializers.SerializerMethodField(read_only=True,)
    subtypes = serializers.SerializerMethodField(read_only=True)
    description = serializers.CharField(read_only=True, source="html_description")
    isFull = serializers.SerializerMethodField(read_only=True,)
    isCertified = serializers.BooleanField(read_only=True, source="is_certified")
    is2022Certified = serializers.BooleanField(
        read_only=True, source="is_2022_certified"
    )
    location = LocationSerializer(read_only=True, source="*")
    contact = ContactMixinSerializer(source="*")
    image = serializers.ImageField(read_only=True)

    referents = serializers.SerializerMethodField(read_only=True,)
    links = serializers.SerializerMethodField(read_only=True,)

    facts = serializers.SerializerMethodField(read_only=True,)
    iconConfiguration = serializers.SerializerMethodField(read_only=True,)

    routes = serializers.SerializerMethodField(read_only=True,)
    discountCodes = serializers.SerializerMethodField(read_only=True,)
    commune = serializers.SerializerMethodField(read_only=True,)

    hasUpcomingEvents = serializers.SerializerMethodField(read_only=True,)
    hasPastEvents = serializers.SerializerMethodField(read_only=True,)
    hasPastEventReports = serializers.SerializerMethodField(read_only=True,)
    hasMessages = serializers.SerializerMethodField(read_only=True,)

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

    def get_isActiveMember(self, obj):
        return self.membership is not None and self.membership.is_active_member

    def get_isManager(self, obj):
        return (
            self.membership is not None
            and self.membership.membership_type >= Membership.MEMBERSHIP_TYPE_MANAGER
        )

    def get_isReferent(self, obj):
        return (
            self.membership is not None
            and self.membership.membership_type >= Membership.MEMBERSHIP_TYPE_REFERENT
        )

    def get_type(self, obj):
        return obj.get_type_display()

    def get_subtypes(self, obj):
        return (
            obj.subtypes.filter(description__isnull=False, hide_text_label=False)
            .exclude(label__in=settings.CERTIFIED_GROUP_SUBTYPES)
            .values_list("description", flat=True)
        )

    def get_isFull(self, obj):
        return obj.is_full

    def get_referents(self, obj):
        return PersonSerializer(
            obj.referents,
            context=self.context,
            many=True,
            fields=["id", "displayName", "image", "gender",],
        ).data

    def get_facts(self, obj):
        facts = {
            "activeMemberCount": obj.active_members_count,
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
        routes = {
            "details": front_url("view_group", kwargs={"pk": obj.pk}),
        }
        if obj.is_certified:
            routes["donations"] = front_url("donation_amount", query={"group": obj.pk})
        if self.membership is not None:
            routes["quit"] = front_url("quit_group", kwargs={"pk": obj.pk})
        if (
            self.membership is not None
            and self.membership.membership_type >= Membership.MEMBERSHIP_TYPE_MANAGER
        ):
            routes["createEvent"] = f'{front_url("create_event")}?group={str(obj.pk)}'
            routes["createSpendingRequest"] = front_url(
                "create_spending_request", kwargs={"group_id": obj.pk}
            )
            routes["settings"] = front_url("view_group_settings", kwargs={"pk": obj.pk})
            routes["edit"] = front_url(
                "view_group_settings_general", kwargs={"pk": obj.pk}
            )
            routes["members"] = front_url(
                "view_group_settings_members", kwargs={"pk": obj.pk}
            )
            routes["membershipTransfer"] = front_url(
                "transfer_group_members", kwargs={"pk": obj.pk}
            )
            routes["geolocate"] = front_url(
                "change_group_location", kwargs={"pk": obj.pk}
            )
            routes["invitation"] = front_url(
                "view_group_settings_contact", kwargs={"pk": obj.pk},
            )
            routes["orders"] = "https://materiel.lafranceinsoumise.fr/"
            if obj.tags.filter(label=settings.PROMO_CODE_TAG).exists():
                routes["materiel"] = front_url(
                    "view_group_settings_materiel", kwargs={"pk": obj.pk}
                )
            if obj.is_certified:
                routes["financement"] = front_url(
                    "view_group_settings_finance", kwargs={"pk": obj.pk},
                )
        if (
            self.membership is not None
            and self.membership.membership_type >= Membership.MEMBERSHIP_TYPE_REFERENT
        ):
            routes["animation"] = front_url(
                "view_group_settings_management", kwargs={"pk": obj.pk}
            )
            routes[
                "animationChangeRequest"
            ] = "https://actionpopulaire.fr/formulaires/demande-changement-animation-ga/"
            routes[
                "referentResignmentRequest"
            ] = "https://infos.actionpopulaire.fr/contact/"
            routes[
                "deleteGroup"
            ] = "https://actionpopulaire.fr/formulaires/demande-suppression-ga/"
            if (
                not obj.is_certified
                and len(obj.referents) >= 2
                and (
                    obj.type in settings.CERTIFIABLE_GROUP_TYPES
                    or obj.subtypes.filter(
                        label__in=settings.CERTIFIABLE_GROUP_SUBTYPES
                    ).exists()
                )
            ):
                certification_request_url = "https://lafranceinsoumise.fr/groupes-appui/demande-de-certification/"
                certification_request_params = {
                    "group-id": obj.pk,
                    "email": self.membership.person.email,
                    "animateur": self.membership.person.get_full_name(),
                }
                routes[
                    "certificationRequest"
                ] = f"{certification_request_url}?{urlencode(certification_request_params)}"
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

    def get_commune(self, obj):
        commune = get_commune(obj)
        if commune is not None:
            commune = {
                "name": commune.nom_complet,
                "nameOf": commune.nom_avec_charniere,
            }
        return commune

    def get_hasUpcomingEvents(self, obj):
        return obj.organized_events.upcoming().exists()

    def get_hasPastEvents(self, obj):
        return obj.organized_events.past().exists()

    def get_hasPastEventReports(self, obj):
        return obj.organized_events.past().exclude(report_content="").exists()

    def get_hasMessages(self, obj):
        return (
            self.membership is not None and obj.messages.filter(deleted=False).exists()
        )

    def get_links(self, obj):
        return obj.links.values("id", "label", "url")


class SupportGroupAdvancedSerializer(SupportGroupDetailSerializer):
    contact = NestedContactSerializer(source="*")


class SupportGroupUpdateSerializer(serializers.ModelSerializer):
    contact = NestedContactSerializer(source="*")
    location = NestedLocationSerializer(source="*")
    image = serializers.ImageField(allow_empty_file=True, allow_null=True)

    class Meta:
        model = SupportGroup
        fields = ["name", "description", "image", "contact", "location"]

    def update(self, instance, validated_data):
        changed_data = {}
        for field, value in validated_data.items():
            new_value = value
            old_value = getattr(instance, field)
            if new_value != old_value:
                changed_data[field] = new_value

        if not changed_data:
            return instance

        instance = super().update(instance, validated_data)
        if "image" in changed_data and changed_data.get("image", None):
            changed_data["image"] = instance.image.url

        if (
            "location_address1" in changed_data
            or "location_address2" in changed_data
            or "location_zip" in changed_data
            or "location_city" in changed_data
            or "location_country" in changed_data
        ):
            geocode_support_group.delay(instance.pk)

        send_support_group_changed_notification.delay(instance.pk, changed_data)

        return instance


class MembershipSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    displayName = serializers.CharField(source="person.display_name", read_only=True)
    email = serializers.EmailField(source="person.email", read_only=True)
    image = serializers.ImageField(source="person.image", read_only=True)
    gender = serializers.CharField(source="person.gender", read_only=True)
    membershipType = serializers.ChoiceField(
        source="membership_type", choices=Membership.MEMBERSHIP_TYPE_CHOICES
    )

    def validate(self, data):
        membership_type = data.get("membership_type", None)

        # Validate maximum number of referents per group
        if (
            membership_type is not None
            and self.instance is not None
            and not self.instance.membership_type == Membership.MEMBERSHIP_TYPE_REFERENT
            and membership_type >= Membership.MEMBERSHIP_TYPE_REFERENT
            and Membership.objects.filter(
                supportgroup=self.instance.supportgroup,
                membership_type__gte=Membership.MEMBERSHIP_TYPE_REFERENT,
            ).count()
            >= 2
        ):
            raise ValidationError(
                detail={
                    "membershipType": "Vous ne pouvez pas ajouter plus de deux animateur·ices"
                }
            )

        return data

    def update(self, instance, validated_data):
        was_active_member = instance.is_active_member
        instance = super().update(instance, validated_data)
        if was_active_member and not instance.is_active_member:
            member_to_follower_notification(instance)
        return instance

    class Meta:
        model = Membership
        fields = ["id", "displayName", "image", "email", "gender", "membershipType"]


class SupportGroupExternalLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportGroupExternalLink
        fields = ["id", "label", "url"]
