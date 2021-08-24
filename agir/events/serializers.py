from datetime import timedelta
from pathlib import PurePath

from django.db import transaction
from django.utils import timezone
from pytz import utc, InvalidTimeError
from rest_framework import serializers

from agir.front.serializer_utils import RoutesField
from agir.lib.serializers import (
    LocationSerializer,
    NestedLocationSerializer,
    NestedContactSerializer,
    FlexibleFieldsMixin,
    CurrentPersonField,
)
from . import models
from .actions.required_documents import (
    get_project_document_deadline,
    get_is_blocking_project,
    get_project_missing_document_count,
)
from .models import (
    Event,
    EventSubtype,
    OrganizerConfig,
    RSVP,
    jitsi_default_domain,
    jitsi_default_room_name,
)
from .tasks import (
    send_event_creation_notification,
    send_secretariat_notification,
    geocode_event,
)
from ..gestion.models import Projet, Document
from ..groups.models import Membership, SupportGroup
from ..groups.serializers import SupportGroupSerializer, SupportGroupDetailSerializer
from ..people.serializers import PersonSerializer
from ..groups.tasks import notify_new_group_event, send_new_group_event_email
from ..lib.utils import admin_url


class EventSubtypeSerializer(serializers.ModelSerializer):
    iconName = serializers.SerializerMethodField(read_only=True)
    icon = serializers.SerializerMethodField(read_only=True)
    color = serializers.SerializerMethodField(read_only=True)
    needsDocuments = serializers.SerializerMethodField(read_only=True)

    def get_needsDocuments(self, obj):
        return obj.related_project_type is not None

    def get_iconName(self, obj):
        return obj.icon_name or obj.TYPES_PARAMETERS[obj.type]["icon_name"]

    def get_color(self, obj):
        return obj.color or obj.TYPES_PARAMETERS[obj.type]["color"]

    def get_icon(self, obj):
        if obj.icon:
            return {
                "iconUrl": obj.icon.url,
                "iconAnchor": [obj.icon_anchor_x or 0, obj.icon_anchor_y or 0],
                "popupAnchor": obj.popup_anchor_y,
            }

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
            "needsDocuments",
        )


EVENT_ROUTES = {
    "details": "view_event",
    "map": "carte:single_event_map",
    "rsvp": "rsvp_event",
    "cancel": "quit_event",
    "manage": "view_event_settings_general",
    "manageMobile": "view_event_settings",
    "calendarExport": "ics_event",
    "compteRendu": "edit_event_report",
    "addPhoto": "upload_event_image",
    "edit": "edit_event",
}


class EventOptionsSerializer(serializers.Serializer):
    price = serializers.SerializerMethodField()

    def get_price(self, obj):
        return obj.get_price_display()


class EventSerializer(FlexibleFieldsMixin, serializers.Serializer):
    EVENT_CARD_FIELDS = [
        "id",
        "name",
        "illustration",
        "hasSubscriptionForm",
        "startTime",
        "endTime",
        "timezone",
        "location",
        "isOrganizer",
        "rsvp",
        "routes",
        "groups",
        "participants",
        "organizers",
        "distance",
        "compteRendu",
        "subtype",
        "onlineUrl",
    ]

    id = serializers.UUIDField()
    url = serializers.HyperlinkedIdentityField(view_name="view_event")
    name = serializers.CharField()
    hasSubscriptionForm = serializers.SerializerMethodField()

    description = serializers.CharField(source="html_description")
    compteRendu = serializers.CharField(source="report_content")
    compteRenduPhotos = serializers.SerializerMethodField()
    illustration = serializers.SerializerMethodField()

    startTime = serializers.SerializerMethodField()
    endTime = serializers.SerializerMethodField()
    timezone = serializers.CharField()

    location = LocationSerializer(source="*")

    isOrganizer = serializers.SerializerMethodField()
    rsvp = serializers.SerializerMethodField()

    options = EventOptionsSerializer(source="*")

    routes = RoutesField(routes=EVENT_ROUTES)

    groups = serializers.SerializerMethodField()

    participants = serializers.SerializerMethodField()

    organizers = serializers.SerializerMethodField()

    contact = NestedContactSerializer(source="*")

    distance = serializers.SerializerMethodField()

    subtype = EventSubtypeSerializer()

    allowGuests = serializers.BooleanField(source="allow_guests")

    onlineUrl = serializers.URLField(source="online_url")

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

    def get_startTime(self, obj):
        return obj.local_start_time.isoformat()

    def get_endTime(self, obj):
        return obj.local_end_time.isoformat()

    def get_hasSubscriptionForm(self, obj):
        return bool(obj.subscription_form_id)

    def get_isOrganizer(self, obj):
        return bool(self.organizer_config)

    def get_rsvp(self, obj):
        return self.rsvp and self.rsvp.status

    def get_compteRenduPhotos(self, obj):
        return [
            {
                "image": instance.image.url,
                "thumbnail": instance.image.thumbnail.url,
                "legend": instance.legend,
            }
            for instance in obj.images.all()
        ]

    def get_routes(self, obj):
        routes = {}
        user = self.context["request"].user

        if user.is_staff and user.has_perm("events.change_event"):
            routes["admin"] = admin_url("events_event_change", args=[obj.pk])

        if obj.facebook:
            routes["facebook"] = obj.facebook

        routes["googleExport"] = obj.get_google_calendar_url()

        return routes

    def get_distance(self, obj):
        if hasattr(obj, "distance") and obj.distance is not None:
            return obj.distance.m

    def get_illustration(self, obj):
        if obj.image:
            return {
                "thumbnail": obj.image.thumbnail.url,
                "banner": obj.image.banner.url,
            }

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

    def get_participants(self, obj):
        return None

    def get_organizers(self, obj):
        return None


class EventAdvancedSerializer(EventSerializer):
    def get_participants(self, obj):
        return PersonSerializer(
            obj.attendees,
            context=self.context,
            many=True,
            fields=["id", "email", "firstName", "lastName", "displayName"],
        ).data

    def get_organizers(self, obj):
        return PersonSerializer(
            obj.organizers,
            context=self.context,
            many=True,
            fields=["id", "email", "firstName", "lastName", "displayName"],
        ).data


class EventListSerializer(EventSerializer):
    def get_groups(self, obj):
        return SupportGroupSerializer(
            obj.organizers_groups.distinct(),
            context=self.context,
            many=True,
            fields=["id", "name", "isMember"],
        ).data


class EventPropertyOptionsSerializer(FlexibleFieldsMixin, serializers.Serializer):
    organizerGroup = serializers.SerializerMethodField()
    subtype = serializers.SerializerMethodField()
    defaultContact = serializers.SerializerMethodField()
    onlineUrl = serializers.SerializerMethodField()

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
            fields=["id", "name", "contact", "location", "isCertified"],
        ).data

    def get_subtype(self, request):
        return EventSubtypeSerializer(
            EventSubtype.objects.filter(
                visibility=EventSubtype.VISIBILITY_ALL
            ).distinct(),
            context=self.context,
            many=True,
        ).data

    def get_defaultContact(self, request):
        contact = {
            "hidePhone": False,
        }
        if self.person and self.person.display_name:
            contact["name"] = self.person.display_name
        if self.person and self.person.contact_phone:
            contact["phone"] = str(self.person.contact_phone)
        if self.person and self.person.email:
            contact["email"] = self.person.email
        return contact

    def get_onlineUrl(self, request):
        return "https://" + jitsi_default_domain() + "/" + jitsi_default_room_name()


class EventOrganizerGroupField(serializers.RelatedField):
    queryset = SupportGroup.objects.all()

    def to_representation(self, obj):
        if obj is None:
            return None
        return SupportGroupSerializer(
            obj, context=self.context, fields=["id", "name", "contact", "location"],
        ).data

    def to_internal_value(self, pk):
        if pk is None:
            return None
        return self.queryset.model.objects.get(pk=pk)


class DateTimeWithTimezoneField(serializers.DateTimeField):
    def enforce_timezone(self, value):
        field_timezone = getattr(self, "timezone", self.default_timezone())

        if field_timezone is not None and not timezone.is_aware(value):
            try:
                return timezone.make_aware(value, field_timezone)
            except InvalidTimeError:
                self.fail("make_aware", timezone=field_timezone)
        elif (field_timezone is None) and timezone.is_aware(value):
            return timezone.make_naive(value, utc)
        return value


class CreateEventSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    url = serializers.HyperlinkedIdentityField(
        read_only=True, view_name="api_event_view"
    )

    name = serializers.CharField(max_length=100, min_length=3)
    timezone = serializers.CharField()
    startTime = DateTimeWithTimezoneField(source="start_time")
    endTime = DateTimeWithTimezoneField(source="end_time")
    contact = NestedContactSerializer(source="*")
    location = NestedLocationSerializer(source="*")
    subtype = serializers.PrimaryKeyRelatedField(
        queryset=EventSubtype.objects.filter(visibility=EventSubtype.VISIBILITY_ALL),
    )
    organizerGroup = EventOrganizerGroupField(
        write_only=True, required=False, allow_null=True
    )
    organizerPerson = CurrentPersonField()
    onlineUrl = serializers.URLField(
        source="online_url", required=False, allow_blank=True
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

        data["organizer_person"] = data.pop("organizerPerson")
        data["organizer_group"] = data.pop("organizerGroup")

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
        if data["organizer_group"]:
            notify_new_group_event.delay(data["organizer_group"].pk, event.pk)
            send_new_group_event_email.delay(data["organizer_group"].pk, event.pk)

    def create(self, validated_data):
        with transaction.atomic():
            event = Event.objects.create(**validated_data)
            # Create a gestion project if needed for the event's subtype
            if event.subtype.related_project_type is not None:
                Projet.objects.from_event(event, event.organizers.first().role)
            self.schedule_tasks(event, validated_data)
            return event


class UpdateEventSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    subtype = serializers.PrimaryKeyRelatedField(
        queryset=EventSubtype.objects.filter(visibility=EventSubtype.VISIBILITY_ALL),
    )
    startTime = DateTimeWithTimezoneField(source="start_time")
    endTime = DateTimeWithTimezoneField(source="end_time")
    onlineUrl = serializers.URLField(source="online_url")
    contact = NestedContactSerializer(source="*")
    location = LocationSerializer(source="*")
    compteRendu = serializers.CharField(source="report_content")
    # compteRenduPhotos = serializers.CharField(source="report_image")

    class Meta:
        model = Event
        fields = [
            "id",
            "name",
            "subtype",
            "description",
            "image",
            "startTime",
            "endTime",
            "timezone",
            "facebook",
            "onlineUrl",
            "contact",
            "location",
            "compteRendu",
            # "compteRenduPhotos"
        ]

    def update(self, instance, validated_data):
        with transaction.atomic():
            event = super().update(instance, validated_data)
            if Projet.objects.filter(event=event).exists():
                Projet.objects.from_event(event, event.organizers.first().role)
            return event


class EventProjectDocumentSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="titre", max_length=200)
    file = serializers.FileField(source="fichier")

    def validate_file(self, value):
        ext = PurePath(value.name).suffix
        if ext.lower() not in [".pdf", ".jpg", ".jpeg", ".png", ".docx"]:
            raise serializers.ValidationError(
                detail="Format de fichier incorrect, seuls .PDF, .JPG, .PNG et .DOCX sont autorisés",
                code="formulaire_format_incorrect",
            )
        return value

    class Meta:
        model = Document
        fields = ["id", "name", "type", "description", "file"]


class ProjectEventSerializer(serializers.ModelSerializer):
    endTime = serializers.DateTimeField(source="end_time", read_only=True)
    subtype = EventSubtypeSerializer(read_only=True)

    class Meta:
        model = Event
        fields = ["id", "name", "endTime", "subtype"]


class EventProjectSerializer(serializers.ModelSerializer):
    projectId = serializers.IntegerField(source="id", read_only=True)
    event = ProjectEventSerializer(read_only=True)
    status = serializers.CharField(source="etat", read_only=True)
    dismissedDocumentTypes = serializers.JSONField(
        source="details.documents.absent", default=list,
    )
    requiredDocumentTypes = serializers.JSONField(
        source="event.subtype.required_documents", read_only=True
    )
    documents = serializers.SerializerMethodField(read_only=True)
    limitDate = serializers.SerializerMethodField(read_only=True)
    isBlocking = serializers.SerializerMethodField(read_only=True)

    def validate_dismissedDocumentTypes(self, types):
        if not isinstance(types, list):
            raise serializers.ValidationError("Format invalide")
        invalid_types = [t for t in types if t not in self.Meta.valid_document_types]
        if len(invalid_types) > 0:
            raise serializers.ValidationError(
                f"Valeurs non autorisée : {','.join(invalid_types)}"
            )

        return types

    def validate(self, data):
        if (
            data.get("details")
            and data["details"].get("documents")
            and data["details"]["documents"].get("absent")
        ):
            dismissed_document_types = data["details"]["documents"].get("absent")
            data.update({"details": self.instance.details})
            if data["details"].get("documents") is None:
                data["details"]["documents"] = {}
            data["details"]["documents"]["absent"] = dismissed_document_types

        return super().validate(data)

    def get_documents(self, obj):
        uploaded_documents = obj.documents.filter(
            type__in=self.Meta.valid_document_types
        )
        return EventProjectDocumentSerializer(
            uploaded_documents, many=True, context=self.context,
        ).data

    def get_limitDate(self, obj):
        return get_project_document_deadline(obj)

    def get_isBlocking(self, obj):
        return get_is_blocking_project(obj)

    class Meta:
        model = Projet
        fields = [
            "projectId",
            "event",
            "status",
            "dismissedDocumentTypes",
            "requiredDocumentTypes",
            "documents",
            "limitDate",
            "isBlocking",
        ]
        valid_document_types = [
            choice[0]
            for choice in EventSubtype.EVENT_SUBTYPE_REQUIRED_DOCUMENT_TYPE_CHOICES
        ]


class EventProjectListItemSerializer(serializers.ModelSerializer):
    projectId = serializers.IntegerField(source="id", read_only=True)
    event = ProjectEventSerializer(read_only=True)
    status = serializers.CharField(source="etat", read_only=True)
    limitDate = serializers.SerializerMethodField(read_only=True)
    missingDocumentCount = serializers.SerializerMethodField(read_only=True)
    isBlocking = serializers.SerializerMethodField(read_only=True)

    def get_limitDate(self, obj):
        return get_project_document_deadline(obj)

    def get_missingDocumentCount(self, obj):
        return get_project_missing_document_count(obj)

    def get_isBlocking(self, obj):
        return get_is_blocking_project(obj)

    class Meta:
        model = Projet
        fields = [
            "projectId",
            "event",
            "status",
            "missingDocumentCount",
            "limitDate",
            "isBlocking",
        ]
        valid_document_types = [
            choice[0]
            for choice in EventSubtype.EVENT_SUBTYPE_REQUIRED_DOCUMENT_TYPE_CHOICES
        ]
