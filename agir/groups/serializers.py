from django.conf import settings
from django_countries.serializers import CountryFieldMixin
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from agir.groups.tasks import (
    send_support_group_changed_notification,
    geocode_support_group,
)
from agir.lib.geo import get_commune
from agir.lib.html import textify
from agir.lib.serializers import (
    FlexibleFieldsMixin,
    LocationSerializer,
    ContactMixinSerializer,
    NestedContactSerializer,
    NestedLocationSerializer,
    PhoneField,
    SimpleLocationSerializer,
)
from agir.people.serializers import PersonSerializer
from . import models
from .actions import get_promo_codes
from .actions.notifications import member_to_follower_notification
from .models import Membership, SupportGroup, SupportGroupExternalLink
from .utils.certification import (
    check_certification_criteria,
)
from .utils.supportgroup import get_supportgroup_routes
from ..front.serializer_utils import RoutesField
from ..people.models import Person


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

    eventCount = serializers.SerializerMethodField(read_only=True)
    membersCount = serializers.SerializerMethodField(read_only=True)
    isMember = serializers.SerializerMethodField(read_only=True)
    isActiveMember = serializers.SerializerMethodField(
        read_only=True,
    )
    isManager = serializers.SerializerMethodField(read_only=True)
    labels = serializers.SerializerMethodField(read_only=True)

    discountCodes = serializers.SerializerMethodField(read_only=True)
    isFull = serializers.BooleanField(source="is_full", read_only=True)
    isOpen = serializers.BooleanField(source="open", read_only=True)
    isEditable = serializers.BooleanField(source="editable", read_only=True)

    routes = RoutesField(routes=GROUP_ROUTES, read_only=True)
    isCertified = serializers.SerializerMethodField(
        read_only=True, method_name="get_is_certified"
    )
    location = SimpleLocationSerializer(source="*", read_only=True)

    def to_representation(self, instance):
        user = self.context["request"].user
        self.membership = None
        if (
            hasattr(instance, "person_membership_type")
            and instance.person_membership_type is not None
        ):
            self.membership = Membership(
                person=user.person,
                supportgroup=instance,
                membership_type=instance.person_membership_type,
            )
        elif (
            not user.is_anonymous
            and hasattr(user, "person")
            and user.person is not None
        ):
            self.membership = (
                instance.memberships.active().filter(person=user.person).first()
            )

        return super().to_representation(instance)

    def get_membersCount(self, obj):
        return obj.active_members_count

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
            self.membership is None
            or self.membership.membership_type < Membership.MEMBERSHIP_TYPE_MANAGER
        ):
            return []

        has_promo_codes = (
            obj.has_promo_codes
            if hasattr(obj, "has_promo_codes")
            else obj.tags.filter(label=settings.PROMO_CODE_TAG).exists()
        )

        if not has_promo_codes:
            return []

        return get_promo_codes(obj)

    def get_eventCount(self, obj):
        return obj.events_count

    def get_is_certified(self, obj):
        if obj.type != SupportGroup.TYPE_LOCAL_GROUP:
            return False
        if hasattr(obj, "has_certification_subtype"):
            return obj.has_certification_subtype
        return obj.is_certified


class SupportGroupDetailSerializer(FlexibleFieldsMixin, serializers.Serializer):
    NON_MANAGER_FIELDS = (
        "id",
        "isMember",
        "isActiveMember",
        "isManager",
        "isReferent",
        "personalInfoConsent",
        "name",
        "type",
        "subtypes",
        "description",
        "textDescription",
        "isFull",
        "isOpen",
        "isCertified",
        "location",
        "contact",
        "image",
        "referents",
        "links",
        "facts",
        "iconConfiguration",
        "routes",
        "commune",
        "hasUpcomingEvents",
        "hasPastEvents",
        "hasPastEventReports",
        "hasMessages",
        "isMessagingEnabled",
        "isBoucleDepartementale",
    )
    id = serializers.UUIDField(
        read_only=True,
    )

    isMember = serializers.SerializerMethodField(
        read_only=True,
    )
    isActiveMember = serializers.SerializerMethodField(
        read_only=True,
    )
    isManager = serializers.SerializerMethodField(
        read_only=True,
    )
    isReferent = serializers.SerializerMethodField(
        read_only=True,
    )
    personalInfoConsent = serializers.SerializerMethodField(read_only=True)

    name = serializers.CharField(
        read_only=True,
    )
    type = serializers.SerializerMethodField(
        read_only=True,
    )
    subtypes = serializers.SerializerMethodField(read_only=True)
    description = serializers.CharField(read_only=True, source="html_description")
    textDescription = serializers.SerializerMethodField(read_only=True)
    isFull = serializers.BooleanField(source="is_full", read_only=True)
    isOpen = serializers.BooleanField(source="open", read_only=True)
    isEditable = serializers.BooleanField(source="editable", read_only=True)
    isCertifiable = serializers.BooleanField(read_only=True, source="is_certifiable")
    certificationCriteria = serializers.SerializerMethodField(read_only=True)
    isCertified = serializers.SerializerMethodField(
        read_only=True, method_name="get_is_certified"
    )
    location = LocationSerializer(read_only=True, source="*")
    contact = serializers.SerializerMethodField(
        read_only=True,
    )
    image = serializers.ImageField(read_only=True)

    referents = serializers.SerializerMethodField(
        read_only=True,
    )
    links = serializers.SerializerMethodField(
        read_only=True,
    )

    facts = serializers.SerializerMethodField(
        read_only=True,
    )
    iconConfiguration = serializers.SerializerMethodField(
        read_only=True,
    )

    routes = serializers.SerializerMethodField(
        read_only=True,
    )
    discountCodes = serializers.SerializerMethodField(
        read_only=True,
    )
    commune = serializers.SerializerMethodField(
        read_only=True,
    )

    hasUpcomingEvents = serializers.SerializerMethodField(
        read_only=True,
    )
    hasPastEvents = serializers.SerializerMethodField(
        read_only=True,
    )
    hasPastEventReports = serializers.SerializerMethodField(
        read_only=True,
    )
    hasMessages = serializers.SerializerMethodField(
        read_only=True,
    )
    isMessagingEnabled = serializers.BooleanField(
        source="is_private_messaging_enabled", read_only=True
    )
    isBoucleDepartementale = serializers.SerializerMethodField(
        method_name="get_is_boucle_departementale", read_only=True
    )

    def get_membership(self, obj):
        user = self.context["request"].user
        self.user = user
        if hasattr(self, "membership"):
            return self.membership

        self.membership = None
        if (
            not user.is_anonymous
            and hasattr(user, "person")
            and user.person is not None
        ):
            self.membership = (
                obj.memberships.active().filter(person_id=user.person.id).first()
            )
        return self.membership

    def get_isMember(self, obj):
        membership = self.get_membership(obj)
        return membership is not None

    def get_isActiveMember(self, obj):
        membership = self.get_membership(obj)
        return membership is not None and membership.is_active_member

    def get_isManager(self, obj):
        membership = self.get_membership(obj)
        return (
            membership is not None
            and membership.membership_type >= Membership.MEMBERSHIP_TYPE_MANAGER
        )

    def get_isReferent(self, obj):
        membership = self.get_membership(obj)
        return (
            membership is not None
            and membership.membership_type >= Membership.MEMBERSHIP_TYPE_REFERENT
        )

    def get_personalInfoConsent(self, obj):
        membership = self.get_membership(obj)
        return (
            membership is not None and membership.personal_information_sharing_consent
        )

    def get_contact(self, instance):
        if self.get_isManager(instance):
            return NestedContactSerializer(
                source="*", context=self.context
            ).to_representation(instance)
        return ContactMixinSerializer(
            source="*", context=self.context
        ).to_representation(instance)

    def get_type(self, obj):
        return obj.get_type_display()

    def get_subtypes(self, obj):
        return (
            obj.subtypes.filter(description__isnull=False, hide_text_label=False)
            .active()
            .values_list("description", flat=True)
        )

    def get_referents(self, obj):
        return PersonSerializer(
            obj.referents,
            context=self.context,
            many=True,
            fields=[
                "id",
                "displayName",
                "image",
                "gender",
            ],
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
        membership = self.get_membership(obj)
        return get_supportgroup_routes(obj, membership, self.user)

    def get_discountCodes(self, obj):
        membership = self.get_membership(obj)
        if (
            membership is not None
            and membership.membership_type >= Membership.MEMBERSHIP_TYPE_MANAGER
            and obj.tags.filter(label=settings.PROMO_CODE_TAG).exists()
        ):
            return get_promo_codes(obj)
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
        membership = self.get_membership(obj)
        return membership is not None and obj.messages.filter(deleted=False).exists()

    def get_links(self, obj):
        return obj.links.values("id", "label", "url")

    def get_textDescription(self, obj):
        if isinstance(obj.description, str):
            return textify(obj.description)
        return ""

    def get_certificationCriteria(self, obj):
        return check_certification_criteria(obj, with_labels=True)

    def get_is_certified(self, obj):
        if obj.type != SupportGroup.TYPE_LOCAL_GROUP:
            return False
        if hasattr(obj, "has_certification_subtype"):
            return obj.has_certification_subtype
        return obj.is_certified

    def get_is_boucle_departementale(self, obj):
        return obj.type == SupportGroup.TYPE_BOUCLE_DEPARTEMENTALE


class SupportGroupSearchResultSerializer(serializers.ModelSerializer):
    location = LocationSerializer(read_only=True, source="*")
    iconConfiguration = serializers.SerializerMethodField(
        read_only=True, method_name="get_icon_configuration"
    )

    def get_icon_configuration(self, obj):
        if obj.type in models.SupportGroup.TYPE_PARAMETERS:
            configuration = models.SupportGroup.TYPE_PARAMETERS[obj.type]
            return {
                "color": configuration["color"],
                "iconName": configuration["icon_name"],
            }

    class Meta:
        model = SupportGroup
        fields = (
            "id",
            "name",
            "location",
            "iconConfiguration",
        )


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
    displayName = serializers.SerializerMethodField(read_only=True)
    email = serializers.SerializerMethodField(read_only=True)
    image = serializers.ImageField(source="person.image", read_only=True)
    gender = serializers.CharField(source="person.gender", read_only=True)
    description = serializers.CharField(read_only=True)
    membershipType = serializers.ChoiceField(
        source="membership_type", choices=Membership.MEMBERSHIP_TYPE_CHOICES
    )
    personalInfoConsent = serializers.BooleanField(
        source="personal_information_sharing_consent"
    )
    hasGroupNotifications = serializers.SerializerMethodField(read_only=True)

    def get_displayName(self, membership):
        if membership.personal_information_sharing_consent:
            return membership.person.get_full_name()

        return membership.person.display_name

    def get_email(self, membership):
        if hasattr(membership, "email"):
            return membership.email
        return membership.person.display_email

    def get_hasGroupNotifications(self, membership):
        return membership.subscription_set.exists()

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
        fields = [
            "id",
            "displayName",
            "image",
            "email",
            "gender",
            "description",
            "membershipType",
            "personalInfoConsent",
            "hasGroupNotifications",
            "created",
            "modified",
        ]


class MemberPersonalInformationSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    displayName = serializers.CharField(source="person.display_name", read_only=True)
    firstName = serializers.CharField(source="person.first_name", read_only=True)
    lastName = serializers.CharField(source="person.last_name", read_only=True)
    gender = serializers.CharField(source="person.gender", read_only=True)
    image = serializers.ImageField(
        default=None, source="person.image.thumbnail", read_only=True
    )
    email = serializers.SerializerMethodField(read_only=True)
    phone = PhoneField(source="person.contact_phone", read_only=True)
    address = serializers.CharField(source="person.short_address", read_only=True)
    is2022 = serializers.BooleanField(source="person.is_2022", read_only=True)
    isLiaison = serializers.SerializerMethodField(read_only=True)
    created = serializers.DateTimeField(read_only=True)
    membershipType = serializers.IntegerField(source="membership_type", read_only=True)
    subscriber = serializers.SerializerMethodField(read_only=True)
    hasGroupNotifications = serializers.SerializerMethodField(read_only=True)
    personalInfoConsent = serializers.BooleanField(
        source="personal_information_sharing_consent", read_only=True
    )
    meta = serializers.JSONField(read_only=True)

    def get_subscriber(self, membership):
        meta = membership.person.meta
        if (
            not meta
            or "subscriptions" not in meta
            or "AP" not in meta["subscriptions"]
            or "subscriber" not in meta["subscriptions"]["AP"]
        ):
            return None
        subscriber = Person.objects.filter(
            id=meta["subscriptions"]["AP"]["subscriber"]
        ).first()
        if not subscriber:
            return None
        return subscriber.display_name

    def get_isLiaison(self, membership):
        return Person.NEWSLETTER_2022_LIAISON in membership.person.newsletters

    def get_hasGroupNotifications(self, membership):
        return membership.subscription_set.exists()

    def get_email(self, membership):
        if hasattr(membership, "email"):
            return membership.email
        return membership.person.display_email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove restricted fields if personal_information_sharing_consent value is False
        if self.instance and not self.instance.personal_information_sharing_consent:
            for f in set(self.fields).intersection(self.Meta.restricted_fields):
                del self.fields[f]

    class Meta:
        model = Membership
        fields = (
            "id",
            "displayName",
            "firstName",
            "lastName",
            "gender",
            "image",
            "email",
            "phone",
            "address",
            "created",
            "membershipType",
            "subscriber",
            "is2022",
            "isLiaison",
            "hasGroupNotifications",
            "personalInfoConsent",
            "meta",
        )
        restricted_fields = (
            "firstName",
            "lastName",
            "gender",
            "phone",
            "address",
            "is2022",
            "isLiaison",
            "hasGroupNotifications",
        )


class SupportGroupExternalLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportGroupExternalLink
        fields = ["id", "label", "url"]
