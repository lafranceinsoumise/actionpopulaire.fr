from rest_framework import serializers

from agir.front.serializer_utils import MediaURLField, RoutesField
from agir.lib.serializers import (
    LocationSerializer,
    ContactMixinSerializer,
    FlexibleFieldsMixin,
)
from . import models
from .models import OrganizerConfig, RSVP, Event, EventSubtype
from ..groups.serializers import SupportGroupSerializer, SupportGroupDetailSerializer
from ..groups.models import Membership, SupportGroup


class EventSubtypeSerializer(serializers.ModelSerializer):
    typeLabel = serializers.SerializerMethodField()
    typeDescription = serializers.SerializerMethodField()
    iconName = serializers.CharField(source="icon_name")

    def get_typeLabel(self, obj):
        return dict(EventSubtype.TYPE_CHOICES)[obj.type]

    def get_typeDescription(self, obj):
        return dict(EventSubtype.TYPE_DESCRIPTION)[obj.type]

    class Meta:
        model = models.EventSubtype
        fields = (
            "id",
            "label",
            "description",
            "color",
            "icon",
            "iconName",
            "type",
            "typeLabel",
            "typeDescription",
        )


EVENT_ROUTES = {
    "details": "view_event",
    "map": "carte:single_event_map",
    "rsvp": "rsvp_event",
    "cancel": "quit_event",
    "manage": "manage_event",
    "calendarExport": "ics_event",
    "compteRendu": "edit_event_report",
    "addPhoto": "upload_event_image",
    "edit": "edit_event",
}


class EventOptionsSerializer(serializers.Serializer):
    price = serializers.SerializerMethodField()

    def get_price(self, obj):
        return obj.get_price_display()


class EventListSerializer(serializers.ListSerializer):
    def get_groups(self, obj):
        return SupportGroupSerializer(
            obj.organizers_groups.distinct(),
            context=self.context,
            many=True,
            fields=["name", "isMember"],
        ).data


class EventSerializer(FlexibleFieldsMixin, serializers.Serializer):
    EVENT_CARD_FIELDS = [
        "id",
        "name",
        "startTime",
        "endTime",
        # "participantCount",
        "illustration",
        "schedule",
        "location",
        "rsvp",
        "routes",
    ]

    id = serializers.UUIDField()
    url = serializers.HyperlinkedIdentityField(view_name="view_event")
    name = serializers.CharField()
    hasSubscriptionForm = serializers.SerializerMethodField()

    description = serializers.CharField(source="html_description")
    compteRendu = serializers.CharField(source="report_content")
    compteRenduPhotos = serializers.SerializerMethodField()
    illustration = MediaURLField(source="image")

    startTime = serializers.DateTimeField(source="start_time")
    endTime = serializers.DateTimeField(source="end_time")

    location = LocationSerializer(source="*")

    isOrganizer = serializers.SerializerMethodField()
    rsvp = serializers.SerializerMethodField()
    # participantCount = serializers.IntegerField(source="participants")

    options = EventOptionsSerializer(source="*")

    routes = RoutesField(routes=EVENT_ROUTES)

    groups = serializers.SerializerMethodField()

    contact = ContactMixinSerializer(source="*")

    distance = serializers.SerializerMethodField()

    is2022 = serializers.SerializerMethodField()

    forUsers = serializers.CharField(source="for_users")

    canRSVP = serializers.SerializerMethodField()

    def to_representation(self, instance):
        user = self.context["request"].user

        if user.is_authenticated and user.person:
            # this allow prefetching by queryset annotation for performances
            if not hasattr(instance, "_pf_person_organizer_configs"):
                self.organizer_config = OrganizerConfig.objects.filter(
                    event=instance, person=user.person
                ).first()
            else:
                self.organizer_config = (
                    instance._pf_person_organizer_configs[0]
                    if len(instance._pf_person_organizer_configs)
                    else None
                )
            if not hasattr(instance, "_pf_person_rsvps"):
                self.rsvp = RSVP.objects.filter(
                    event=instance, person=user.person
                ).first()
            else:
                self.rsvp = (
                    instance._pf_person_rsvps[0]
                    if len(instance._pf_person_rsvps)
                    else None
                )
        else:
            self.organizer_config = self.rsvp = None

        return super().to_representation(instance)

    def get_hasSubscriptionForm(self, obj):
        return bool(obj.subscription_form_id)

    def get_isOrganizer(self, obj):
        return bool(self.organizer_config)

    def get_rsvp(self, obj):
        return self.rsvp and self.rsvp.status

    def get_canRSVP(self, obj):
        user = self.context["request"].user
        if hasattr(user, "person"):
            return obj.can_rsvp(user.person)
        return None

    def get_compteRenduPhotos(self, obj):
        return [instance.image.thumbnail.url for instance in obj.images.all()]

    def get_routes(self, obj):
        routes = {}

        if obj.facebook:
            routes["facebook"] = f"https://www.facebook.com/events/{obj.facebook}"

        routes["googleExport"] = obj.get_google_calendar_url()

        return routes

    def get_distance(self, obj):
        if hasattr(obj, "distance") and obj.distance is not None:
            return obj.distance.m

    def get_is2022(self, obj):
        return obj.is_2022

    def get_groups(self, obj):
        return SupportGroupSerializer(
            obj.organizers_groups.distinct(),
            context=self.context,
            many=True,
            fields=[
                "id",
                "name",
                "description",
                "eventCount",
                "membersCount",
                "isMember",
                "isManager",
                "typeLabel",
                "labels",
                "routes",
                "is2022",
            ],
        ).data

    class Meta:
        list_serializer_class = EventListSerializer


class EventCreateOptionsSerializer(FlexibleFieldsMixin, serializers.Serializer):
    organizerGroup = serializers.SerializerMethodField()
    forUsers = serializers.SerializerMethodField()
    subtype = serializers.SerializerMethodField()
    defaultContact = serializers.SerializerMethodField()

    def to_representation(self, instance):
        user = self.context["request"].user
        self.person = None
        if not user.is_anonymous and user.person:
            self.person = user.person
        return super().to_representation(instance)

    def get_organizerGroup(self, request):
        return SupportGroupDetailSerializer(
            SupportGroup.objects.filter(
                memberships__person=self.person,
                memberships__membership_type__gte=Membership.MEMBERSHIP_TYPE_MANAGER,
            ).active(),
            context=self.context,
            many=True,
            fields=["id", "name", "is2022", "contact", "location"],
        ).data

    def get_subtype(self, request):
        return EventSubtypeSerializer(
            EventSubtype.objects.filter(
                visibility=EventSubtype.VISIBILITY_ALL
            ).distinct(),
            context=self.context,
            many=True,
        ).data

    def get_forUsers(self, request):
        options = [
            {"value": Event.FOR_USERS_2022, "label": "La campagne présidentielle",},
            {
                "value": Event.FOR_USERS_INSOUMIS,
                "label": "Une autre campagne France insoumise",
            },
        ]

        if self.person and self.person.is_2022 and not self.person.is_insoumise:
            return options[:1]

        if self.person and not self.person.is_2022 and self.person.is_insoumise:
            return options[1:]

        return options

    def get_defaultContact(self, request):
        contact = {
            "hidePhone": False,
        }
        if self.person and self.person.display_name:
            contact["name"] = self.person.display_name
        if self.person and self.person.contact_phone:
            contact["phone"] = self.person.contact_phone
        if self.person and self.person.email:
            contact["email"] = self.person.email
        return contact
