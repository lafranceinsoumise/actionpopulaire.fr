from django.conf import settings
from django_countries.serializers import CountryFieldMixin
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from agir.groups.tasks import (
    send_support_group_changed_notification,
    geocode_support_group,
)
from agir.lib.html import textify
from agir.lib.serializers import (
    FlexibleFieldsMixin,
    LocationSerializer,
    ContactMixinSerializer,
    NestedContactSerializer,
    NestedLocationSerializer,
    PhoneField,
    SimpleLocationSerializer,
    SnakeToCamelCaseDictField,
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


class SupportGroupExternalLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportGroupExternalLink
        fields = ["id", "label", "url"]


class SupportGroupSerializerMixin(FlexibleFieldsMixin, serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(read_only=True)
    description = serializers.CharField(source="html_description", read_only=True)
    type = serializers.CharField(read_only=True)
    typeLabel = serializers.CharField(source="get_type_display", read_only=True)
    discountCodes = serializers.SerializerMethodField(
        method_name="get_discount_codes", read_only=True
    )
    membershipType = serializers.SerializerMethodField(
        method_name="get_membership_type", read_only=True
    )
    isMember = serializers.SerializerMethodField(
        method_name="is_member", read_only=True
    )
    isActiveMember = serializers.SerializerMethodField(
        method_name="is_active_member", read_only=True
    )
    isManager = serializers.SerializerMethodField(
        method_name="is_manager", read_only=True
    )
    isFinanceManager = serializers.SerializerMethodField(
        method_name="is_finance_manager", read_only=True
    )
    isReferent = serializers.SerializerMethodField(
        method_name="is_referent", read_only=True
    )
    isFull = serializers.BooleanField(source="is_full", read_only=True)
    isOpen = serializers.BooleanField(source="open", read_only=True)
    isEditable = serializers.BooleanField(source="editable", read_only=True)
    isPublished = serializers.BooleanField(source="published", read_only=True)
    isCertified = serializers.BooleanField(source="is_certified", read_only=True)
    isFinanceable = serializers.BooleanField(source="is_financeable", read_only=True)

    @property
    def user(self):
        return self.context["request"].user

    def to_representation(self, obj):
        if getattr(self, "_membership", None):
            # Reset cached current user membership (to allow many=True usage)
            del self._membership

        return super().to_representation(obj)

    def get_membership(self, obj):
        if hasattr(self, "_membership"):
            return self._membership

        self._membership = None

        if getattr(obj, "_pf_person_membership", None):
            self._membership = obj._pf_person_membership[0]
        elif (
            not self.user.is_anonymous
            and hasattr(self.user, "person")
            and self.user.person is not None
        ):
            self._membership = (
                obj.memberships.active().filter(person=self.user.person).first()
            )

        return self._membership

    def get_membership_type(self, obj):
        membership = self.get_membership(obj)
        return membership.membership_type if membership is not None else 0

    def is_member(self, obj):
        membership = self.get_membership(obj)
        return membership is not None

    def is_active_member(self, obj):
        membership = self.get_membership(obj)
        return membership is not None and membership.is_active_member

    def is_manager(self, obj):
        membership = self.get_membership(obj)
        return membership is not None and membership.is_manager

    def is_finance_manager(self, obj):
        membership = self.get_membership(obj)
        return membership is not None and membership.is_finance_manager

    def is_referent(self, obj):
        membership = self.get_membership(obj)
        return membership is not None and membership.is_referent

    def get_discount_codes(self, obj):
        membership = self.get_membership(obj)

        if membership is None or not membership.is_manager:
            return []

        has_promo_codes = (
            obj.has_promo_codes
            if hasattr(obj, "has_promo_codes")
            else obj.tags.filter(label=settings.PROMO_CODE_TAG).exists()
        )

        if not has_promo_codes:
            return []

        return get_promo_codes(obj)


class SupportGroupSerializer(SupportGroupSerializerMixin):
    url = serializers.HyperlinkedIdentityField(view_name="view_group", read_only=True)
    location = SimpleLocationSerializer(source="*", with_address=False)
    eventCount = serializers.IntegerField(source="events_count", read_only=True)
    membersCount = serializers.IntegerField(
        source="active_members_count", read_only=True
    )
    labels = serializers.SerializerMethodField(read_only=True)
    routes = RoutesField(routes=GROUP_ROUTES, read_only=True)

    def get_labels(self, obj):
        return [
            s.description
            for s in obj.subtypes.all()
            if s.description and not s.hide_text_label
        ]


class SupportGroupDetailSerializer(SupportGroupSerializerMixin):
    NON_MANAGER_FIELDS = (
        "id",
        "membershipType",
        "isMember",
        "isActiveMember",
        "isManager",
        "isReferent",
        "personalInfoConsent",
        "name",
        "type",
        "typeLabel",
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
    image = serializers.ImageField(read_only=True)
    personalInfoConsent = serializers.SerializerMethodField(
        method_name="get_personal_info_consent", read_only=True
    )
    location = serializers.SerializerMethodField(read_only=True)
    contact = serializers.SerializerMethodField(read_only=True)
    subtypes = serializers.SerializerMethodField(read_only=True)
    referents = serializers.SerializerMethodField(read_only=True)
    facts = serializers.SerializerMethodField(read_only=True)
    iconConfiguration = SnakeToCamelCaseDictField(
        source="get_icon_configuration", read_only=True
    )
    routes = serializers.SerializerMethodField(read_only=True)
    links = SupportGroupExternalLinkSerializer(many=True, read_only=True)
    textDescription = serializers.SerializerMethodField(
        method_name="get_text_description", read_only=True
    )
    certificationCriteria = serializers.SerializerMethodField(
        method_name="get_certification_criteria", read_only=True
    )
    isCertifiable = serializers.BooleanField(source="is_certifiable", read_only=True)
    hasUpcomingEvents = serializers.SerializerMethodField(
        method_name="has_upcoming_events", read_only=True
    )
    hasPastEvents = serializers.SerializerMethodField(
        method_name="has_past_events", read_only=True
    )
    hasPastEventReports = serializers.SerializerMethodField(
        method_name="has_past_event_reports", read_only=True
    )
    hasMessages = serializers.SerializerMethodField(
        method_name="has_messages", read_only=True
    )
    isBoucleDepartementale = serializers.SerializerMethodField(
        method_name="is_boucle_departementale", read_only=True
    )
    isMessagingEnabled = serializers.BooleanField(
        source="is_private_messaging_enabled", read_only=True
    )

    def get_personal_info_consent(self, obj):
        membership = self.get_membership(obj)
        return (
            membership is not None and membership.personal_information_sharing_consent
        )

    def get_location(self, obj):
        return LocationSerializer(
            source="*", read_only=True, with_address=self.is_manager(obj)
        ).to_representation(obj)

    def get_contact(self, obj):
        if self.is_manager(obj):
            return NestedContactSerializer(
                source="*", context=self.context
            ).to_representation(obj)

        return ContactMixinSerializer(
            source="*", context=self.context
        ).to_representation(obj)

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

    def get_routes(self, obj):
        return get_supportgroup_routes(obj, self.get_membership(obj), self.user)

    def get_text_description(self, obj):
        if isinstance(obj.description, str):
            return textify(obj.description)
        return ""

    def get_certification_criteria(self, obj):
        return check_certification_criteria(obj, with_labels=True)

    def has_upcoming_events(self, obj):
        return obj.organized_events.upcoming().exists()

    def has_past_events(self, obj):
        return obj.organized_events.past().exists()

    def has_past_event_reports(self, obj):
        return obj.organized_events.past().exclude(report_content="").exists()

    def has_messages(self, obj):
        membership = self.get_membership(obj)
        return membership is not None and obj.messages.filter(deleted=False).exists()

    def is_boucle_departementale(self, obj):
        return obj.type == SupportGroup.TYPE_BOUCLE_DEPARTEMENTALE


class SupportGroupSearchResultSerializer(serializers.ModelSerializer):
    location = LocationSerializer(read_only=True, source="*", with_address=False)
    iconConfiguration = SnakeToCamelCaseDictField(
        source="get_icon_configuration", read_only=True
    )

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
    displayName = serializers.SerializerMethodField(
        method_name="get_display_name", read_only=True
    )
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
    hasGroupNotifications = serializers.SerializerMethodField(
        method_name="has_group_notifications", read_only=True
    )
    isFinanceManager = serializers.BooleanField(
        source="is_finance_manager", read_only=True
    )

    def get_display_name(self, membership):
        if membership.personal_information_sharing_consent:
            return membership.person.get_full_name()

        return membership.person.display_name

    def get_email(self, membership):
        if hasattr(membership, "email"):
            return membership.email
        return membership.person.display_email

    def has_group_notifications(self, membership):
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
            "isFinanceManager",
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
    isFinanceManager = serializers.BooleanField(
        source="is_finance_manager", read_only=True
    )
    isPoliticalSupport = serializers.BooleanField(
        source="person.is_political_support", read_only=True
    )
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
        return membership.person.is_liaison

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
            "isPoliticalSupport",
            "isFinanceManager",
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
            "isPoliticalSupport",
            "isLiaison",
            "hasGroupNotifications",
        )
