from datetime import timedelta
from rest_framework import serializers

from agir.front.serializer_utils import MediaURLField, RoutesField
from agir.lib.serializers import (
    LocationSerializer,
    ContactMixinSerializer,
    NestedLocationSerializer,
    NestedContactSerializer,
    FlexibleFieldsMixin,
    CurrentPersonDefault,
)
from . import models
from .actions.legal import needs_approval
from .models import OrganizerConfig, RSVP, Event, EventSubtype
from .tasks import (
    send_event_creation_notification,
    send_secretariat_notification,
    geocode_event,
)
from ..groups.tasks import notify_new_group_event
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


class EventOrganizerGroupField(serializers.RelatedField):
    queryset = SupportGroup.objects.all()

    def to_representation(self, obj):
        if obj is None:
            return None
        return SupportGroupSerializer(
            obj,
            context=self.context,
            fields=["id", "name", "is2022", "contact", "location"],
        ).data

    def to_internal_value(self, pk):
        if pk is None:
            return None
        return self.queryset.model.objects.get(pk=pk)


class CreateEventSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    url = serializers.HyperlinkedIdentityField(
        read_only=True, view_name="api_event_view"
    )

    name = serializers.CharField(max_length=100, min_length=3)
    startTime = serializers.DateTimeField(source="start_time")
    endTime = serializers.DateTimeField(source="end_time")
    contact = NestedContactSerializer(source="*")
    location = NestedLocationSerializer(source="*")
    forUsers = serializers.CharField(source="for_users", required=True)
    subtype = serializers.PrimaryKeyRelatedField(
        queryset=EventSubtype.objects.filter(visibility=EventSubtype.VISIBILITY_ALL),
    )
    organizerGroup = EventOrganizerGroupField(
        write_only=True, required=False, allow_null=True
    )
    organizerPerson = serializers.HiddenField(
        default=CurrentPersonDefault(), write_only=True,
    )

    class Meta:
        model = Event

    def validate(self, data):
        if data.get("organizerGroup") and data["organizerGroup"] is not None:
            if (
                not data["organizerPerson"] in data["organizerGroup"].referents
                and not data["organizerPerson"] in data["organizerGroup"].managers
            ):
                raise serializers.ValidationError(
                    {
                        "organizerGroup": "Veuillez choisir un groupe dont vous êtes animateur·ice"
                    }
                )

        if (
            data.get("end_time")
            and data.get("start_time")
            and data["end_time"] - data["start_time"] > timedelta(days=7)
        ):
            raise serializers.ValidationError(
                {"endTime": "Votre événement doit durer moins d’une semaine"}
            )

        return data

    def schedule_tasks(self, event, data):
        organizer_config = OrganizerConfig.objects.filter(event=event).first()
        # Send the confirmation notification and geolocate the event
        send_event_creation_notification.delay(organizer_config.pk)
        geocode_event.delay(event.pk)
        if event.visibility == Event.VISIBILITY_ORGANIZER:
            send_secretariat_notification.delay(
                organizer_config.event.pk, organizer_config.person.pk, complete=False,
            )
        # Also notify members if it is organized by a group
        if data["organizerGroup"]:
            notify_new_group_event.delay(data["organizerGroup"].pk, event.pk)

    def create(self, validated_data):
        if isinstance(validated_data.get("legal"), dict) and needs_approval(
            validated_data.get("legal")
        ):
            validated_data["visibility"] = Event.VISIBILITY_ORGANIZER

        event = Event.objects.create(
            name=validated_data["name"],
            start_time=validated_data["start_time"],
            end_time=validated_data["end_time"],
            contact_name=validated_data["contact_name"],
            contact_email=validated_data["contact_email"],
            contact_phone=validated_data["contact_phone"],
            contact_hide_phone=validated_data["contact_hide_phone"],
            location_name=validated_data["location_name"],
            location_address1=validated_data["location_address1"],
            location_address2=validated_data["location_address2"],
            location_zip=validated_data["location_zip"],
            location_city=validated_data["location_city"],
            location_country=validated_data["location_country"],
            for_users=validated_data["for_users"],
            subtype=validated_data["subtype"],
            organizer_group=validated_data["organizerGroup"],
            organizer_person=validated_data["organizerPerson"],
        )

        self.schedule_tasks(event, validated_data)

        return event
