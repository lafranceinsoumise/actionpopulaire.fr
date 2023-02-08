from datetime import timedelta
from functools import partial
from pathlib import PurePath

from django.db import transaction
from django.db.models import (
    OuterRef,
    Exists,
    Value,
)
from django.utils import timezone
from pytz import utc, InvalidTimeError
from rest_framework import serializers
from rest_framework.fields import empty

from agir.activity.models import Activity
from agir.events.tasks import NOTIFIED_CHANGES
from agir.front.serializer_utils import RoutesField
from agir.lib.admin.utils import admin_url
from agir.lib.html import textify
from agir.lib.serializers import (
    LocationSerializer,
    NestedLocationSerializer,
    NestedContactSerializer,
    ContactMixinSerializer,
    FlexibleFieldsMixin,
    CurrentPersonField,
)
from agir.lib.utils import replace_datetime_timezone
from agir.lib.utils import (
    validate_facebook_event_url,
    INVALID_FACEBOOK_EVENT_LINK_MESSAGE,
    front_url,
    get_youtube_video_id,
)
from agir.people.person_forms.models import PersonForm
from . import models
from .actions.required_documents import (
    get_project_document_deadline,
    get_is_blocking_project,
    get_project_missing_document_count,
)
from .models import (
    Event,
    EventSubtype,
    Invitation,
    OrganizerConfig,
    RSVP,
    jitsi_default_domain,
    jitsi_default_room_name,
)
from .tasks import (
    send_event_creation_notification,
    send_secretariat_notification,
    geocode_event,
    send_event_changed_notification,
    notify_on_event_report,
)
from ..elections.utils import is_forbidden_during_treve_event
from ..gestion.models import Projet, Document, VersionDocument
from ..groups.models import Membership, SupportGroup
from ..groups.serializers import SupportGroupSerializer, SupportGroupDetailSerializer
from ..groups.tasks import notify_new_group_event, send_new_group_event_email
from ..lib.data import french_zipcode_to_country_code, FRANCE_COUNTRY_CODES

EVENT_ROUTES = {
    "details": "view_event",
    "map": "carte:single_event_map",
    "rsvp": "rsvp_event",
    "cancel": "quit_event",
    "manage": "view_event_settings",
    "calendarExport": "ics_event",
    "compteRendu": "edit_event_report",
    "addPhoto": "upload_event_image",
    "edit": "edit_event",
}


class EventSubtypeSerializer(serializers.ModelSerializer):
    iconName = serializers.SerializerMethodField(read_only=True)
    icon = serializers.SerializerMethodField(read_only=True)
    color = serializers.SerializerMethodField(read_only=True)
    needsDocuments = serializers.SerializerMethodField(read_only=True)
    isVisible = serializers.SerializerMethodField(read_only=True)

    def get_needsDocuments(self, obj):
        return bool(obj.related_project_type)

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

    def get_isVisible(self, obj):
        return obj.visibility == EventSubtype.VISIBILITY_ALL

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
            "isVisible",
        )


class EventOptionsSerializer(serializers.Serializer):
    price = serializers.SerializerMethodField()

    def get_price(self, obj):
        return obj.get_price_display()


class EventSerializer(FlexibleFieldsMixin, serializers.Serializer):
    EVENT_CARD_FIELDS = [
        "id",
        "name",
        "illustration",
        "startTime",
        "endTime",
        "timezone",
        "location",
        "groups",
        "subtype",
        "groupsAttendees",
    ]

    id = serializers.UUIDField()
    url = serializers.HyperlinkedIdentityField(view_name="view_event")
    name = serializers.CharField()
    hasSubscriptionForm = serializers.SerializerMethodField()

    description = serializers.CharField(source="html_description")
    textDescription = serializers.SerializerMethodField()
    compteRendu = serializers.CharField(source="report_content")
    compteRenduMainPhoto = serializers.SerializerMethodField(source="report_image")
    compteRenduPhotos = serializers.SerializerMethodField()

    illustration = serializers.SerializerMethodField()
    metaImage = serializers.SerializerMethodField()

    startTime = serializers.SerializerMethodField()
    endTime = serializers.SerializerMethodField()
    timezone = serializers.CharField()

    location = LocationSerializer(source="*")

    isOrganizer = serializers.SerializerMethodField()
    isManager = serializers.SerializerMethodField()
    isEditable = serializers.BooleanField(source="subtype.is_editable", read_only=True)

    rsvp = serializers.SerializerMethodField()

    options = EventOptionsSerializer(source="*")

    routes = RoutesField(routes=EVENT_ROUTES)

    groups = serializers.SerializerMethodField()

    groupsAttendees = serializers.SerializerMethodField()

    contact = ContactMixinSerializer(source="*")

    distance = serializers.SerializerMethodField()

    subtype = EventSubtypeSerializer()

    allowGuests = serializers.BooleanField(source="allow_guests")

    onlineUrl = serializers.URLField(source="online_url")
    youtubeVideoID = serializers.SerializerMethodField(
        method_name="youtube_video_id", read_only=True
    )

    isPast = serializers.SerializerMethodField(
        read_only=True, method_name="get_is_past"
    )

    hasProject = serializers.SerializerMethodField(
        read_only=True, method_name="get_has_project"
    )

    def __init__(self, instance=None, data=empty, fields=None, **kwargs):
        self.is_event_card = fields == self.EVENT_CARD_FIELDS
        super().__init__(instance=instance, data=data, fields=fields, **kwargs)

    def to_representation(self, instance):
        user = self.context["request"].user

        if not self.is_event_card and user.is_authenticated and user.person:
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
        user = self.context["request"].user

        if not user.is_authenticated or not user.person:
            return False

        if bool(self.organizer_config):
            return True

        if obj.organizers_groups.filter(
            memberships__person=user.person,
            memberships__membership_type__gte=Membership.MEMBERSHIP_TYPE_REFERENT,
        ).exists():
            return True

        return False

    def get_isManager(self, obj):
        user = self.context["request"].user

        if not user.is_authenticated or not user.person:
            return False

        if bool(self.organizer_config):
            return True

        if obj.organizers_groups.filter(
            memberships__person=user.person,
            memberships__membership_type__gte=Membership.MEMBERSHIP_TYPE_MANAGER,
        ).exists():
            return True

        return False

    def get_rsvp(self, obj):
        return self.rsvp and self.rsvp.status

    def get_compteRenduMainPhoto(self, obj):
        if obj.report_image:
            return {
                "image": obj.report_image.url,
                "thumbnail": obj.report_image.thumbnail.url,
                "banner": obj.report_image.banner.url,
            }

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
            obj.organizers_groups.distinct().with_serializer_prefetch(),
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

    def get_groupsAttendees(self, obj):
        user = self.context["request"].user
        if user.is_anonymous or not hasattr(user, "person") or user.person is None:
            self.person = None
            return (
                obj.groups_attendees.all()
                .annotate(isManager=Value(False))
                .values("id", "name", "isManager")
            )

        self.person = user.person
        return (
            obj.groups_attendees.all()
            .annotate(
                isManager=Exists(
                    self.person.memberships.filter(
                        supportgroup_id=OuterRef("id"),
                        membership_type__gte=Membership.MEMBERSHIP_TYPE_MANAGER,
                    )
                )
            )
            .values("id", "name", "isManager")
        )

    def get_is_past(self, obj):
        return obj.is_past()

    def get_has_project(self, obj):
        return Projet.objects.filter(event=obj).exists()

    def get_textDescription(self, obj):
        if isinstance(obj.description, str):
            return textify(obj.description)
        return ""

    def get_metaImage(self, obj):
        return obj.get_meta_image()

    def youtube_video_id(self, obj):
        if obj.online_url:
            try:
                return get_youtube_video_id(obj.online_url)
            except ValueError:
                pass
        return ""


class EventAdvancedSerializer(EventSerializer):
    participants = serializers.SerializerMethodField()
    contact = NestedContactSerializer(source="*")
    groupsInvited = serializers.SerializerMethodField(method_name="get_groups_invited")

    def get_participants(self, obj):
        organizers = {
            str(person.id): {
                "id": person.id,
                "email": person.email,
                "displayName": person.display_name,
                "gender": person.gender,
                "isOrganizer": True,
            }
            for person in obj.organizers.all()
        }
        organizer_group_referents = {
            str(person.id): {
                "id": person.id,
                "email": person.email,
                "displayName": person.display_name,
                "gender": person.gender,
                "isOrganizer": True,
            }
            for person in sum(
                [group.referents for group in obj.organizers_groups.distinct()], []
            )
        }

        other_participants = {
            str(person.id): {
                "id": person.id,
                "email": person.email,
                "displayName": person.display_name,
                "gender": person.gender,
            }
            for person in obj.attendees.all()
        }

        participants = {
            **other_participants,
            **organizer_group_referents,
            **organizers,
        }

        if hasattr(obj, "event_request"):
            speaker_person_ids = [
                str(person_id)
                for person_id in obj.event_request.event_speaker_requests.accepted().values_list(
                    "event_speaker__person_id", flat=True
                )
                if str(person_id) in participants
            ]
            for person_id in speaker_person_ids:
                participants[person_id]["isEventSpeaker"] = True

        return participants.values()

    def get_groups_invited(self, obj):
        groups_invited = SupportGroup.objects.filter(
            invitations__status=Invitation.STATUS_PENDING, invitations__event=obj
        )

        return [
            {
                "id": group.id,
                "name": group.name,
                "description": textify(group.description),
            }
            for group in groups_invited
        ]


class EventListSerializer(EventSerializer):
    def get_groups(self, obj):
        if hasattr(obj, "_pf_organizer_groups"):
            return [
                {"id": group.id, "name": group.name}
                for group in obj._pf_organizer_groups
            ]
        return obj.organizers_groups.distinct().values("id", "name")


class EventPropertyOptionsSerializer(FlexibleFieldsMixin, serializers.Serializer):
    organizerGroup = serializers.SerializerMethodField()
    subtype = serializers.SerializerMethodField()
    defaultContact = serializers.SerializerMethodField()
    # onlineUrl = serializers.SerializerMethodField()

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
    queryset = (
        SupportGroup.objects.active()
        .prefetch_related("subtypes")
        .with_static_map_image()
    )

    def to_representation(self, obj):
        if obj is None:
            return None
        return SupportGroupSerializer(
            obj,
            context=self.context,
            fields=["id", "name", "contact", "location"],
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
        read_only=True, view_name="api_event_details"
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
    image = serializers.ImageField(
        required=False, allow_empty_file=True, allow_null=True
    )
    description = serializers.CharField(
        allow_blank=True, allow_null=False, required=False
    )

    class Meta:
        model = Event

    def validate(self, data):
        if data.get("organizerGroup", None) is not None:
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
                {"endTime": "L'événement ne peut pas durer plus de 7 jours."}
            )

        data["organizer_person"] = data.pop("organizerPerson", None)
        data["organizer_group"] = data.pop("organizerGroup", None)

        if (
            data.get("location_zip")
            and data.get("location_country") in FRANCE_COUNTRY_CODES
        ):
            data["location_country"] = french_zipcode_to_country_code(
                data["location_zip"]
            )

        if is_forbidden_during_treve_event(data):
            raise serializers.ValidationError(
                {
                    "endTime": "Ce type d'événement n'est pas autorisé pendant la trêve électorale"
                }
            )

        return data

    def schedule_tasks(self, event, data):
        organizer_config = OrganizerConfig.objects.filter(event=event).first()
        # Send the confirmation notification and geolocate the event
        send_event_creation_notification.delay(organizer_config.pk)
        geocode_event.delay(event.pk)
        if event.visibility == Event.VISIBILITY_ORGANIZER:
            send_secretariat_notification.delay(
                organizer_config.event.pk,
                organizer_config.person.pk,
                complete=False,
            )
        # Also notify members if it is organized by a group
        if data["organizer_group"]:
            notify_new_group_event.delay(data["organizer_group"].pk, event.pk)
            send_new_group_event_email.delay(data["organizer_group"].pk, event.pk)

    def create(self, validated_data):
        event = Event.objects.create(**validated_data)
        self.schedule_tasks(event, validated_data)
        return event


class UpdateEventSerializer(serializers.ModelSerializer):
    PAST_ONLY_FIELDS = []
    UPCOMING_ONLY_FIELDS = [
        "name",
        "subtype",
        "description",
        "image",
        "startTime",
        "endTime",
        "timezone",
        "facebook",
        "onlineUrl",
        "location",
        "organizerGroup",
    ]

    id = serializers.UUIDField(read_only=True)
    subtype = serializers.PrimaryKeyRelatedField(
        queryset=EventSubtype.objects.filter(visibility=EventSubtype.VISIBILITY_ALL),
        allow_null=True,
    )
    startTime = DateTimeWithTimezoneField(source="start_time")
    endTime = DateTimeWithTimezoneField(source="end_time")
    onlineUrl = serializers.URLField(source="online_url", allow_blank=True)
    facebook = serializers.CharField(allow_blank=True)
    contact = NestedContactSerializer(source="*")
    image = serializers.ImageField(allow_empty_file=True, allow_null=True)
    location = LocationSerializer(source="*")
    compteRendu = serializers.CharField(source="report_content", allow_blank=True)
    compteRenduPhoto = serializers.ImageField(
        source="report_image", allow_empty_file=True, allow_null=True
    )
    organizerGroup = EventOrganizerGroupField(
        write_only=True, required=False, allow_null=True
    )

    def to_internal_value(self, data):
        # Validate fields that can be modified only before / after the event's end
        if self.instance.is_past():
            error_message = "Ce champs ne peut être modifié après la fin de l'événement"
            forbidden_fields = [
                field
                for field, value in data.items()
                if field in self.UPCOMING_ONLY_FIELDS
            ]
        else:
            error_message = "Ce champs ne peut être modifié avant la fin de l'événement"
            forbidden_fields = [
                field for field, value in data.items() if field in self.PAST_ONLY_FIELDS
            ]

        if len(forbidden_fields) > 0:
            errors = {
                field: error_message
                for field in forbidden_fields
                if not isinstance(data[field], dict)
            } | {
                field: {key: error_message for key in data[field].keys()}
                for field in forbidden_fields
                if isinstance(data[field], dict)
            }
            raise serializers.ValidationError(errors)

        return super().to_internal_value(data)

    def validate_contact(self, value):
        if "contact" in self.UPCOMING_ONLY_FIELDS and self.instance.is_past():
            forbidden_fields = [
                field
                for field, value in value.items()
                if field not in self.PAST_ONLY_FIELDS
            ]
            if len(forbidden_fields) > 0:
                raise serializers.ValidationError(
                    {
                        field: "Ce champs ne peut être modifié après la fin de l'événement"
                        for field in forbidden_fields
                    }
                )
        if value and not value.get("contact_email") or value["contact_email"] == "":
            raise serializers.ValidationError(
                detail={"email": "Ce champ ne peut être vide."}
            )
        return value

    def validate_subtype(self, value):
        if value is None or value == "":
            raise serializers.ValidationError(
                detail="Choisir un type d'événement est obligatoire",
            )
        return value

    def validate_facebook(self, value):
        if not value or value == "":
            return value
        if not validate_facebook_event_url(value):
            raise serializers.ValidationError(INVALID_FACEBOOK_EVENT_LINK_MESSAGE)
        return value

    def validate(self, data):
        data["id"] = self.instance.pk
        data["organizerPerson"] = self.context["request"].user.person
        if data.get("organizerGroup", None):
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
            data.get("location_zip")
            and data.get("location_country") in FRANCE_COUNTRY_CODES
        ):
            data["location_country"] = french_zipcode_to_country_code(
                data["location_zip"]
            )

        if is_forbidden_during_treve_event(data):
            raise serializers.ValidationError(
                {
                    "global": "Ce type d'événement n'est pas autorisé pendant la trêve électorale"
                }
            )

        return data

    def schedule_tasks(
        self, event, changed_fields, changed_supportgroup, has_new_report
    ):
        # Update geolocation if address has changed
        if (
            "location_address1" in changed_fields
            or "location_address2" in changed_fields
            or "location_zip" in changed_fields
            or "location_city" in changed_fields
            or "location_country" in changed_fields
        ):
            geocode_event.delay(event.pk)

        # Notify participants if important data changed
        for r in event.attendees.all():
            activity = Activity.objects.filter(
                type=Activity.TYPE_EVENT_UPDATE,
                recipient=r,
                event=event,
                status=Activity.STATUS_UNDISPLAYED,
                created__gt=timezone.now() + timedelta(minutes=2),
            ).first()
            if activity is not None:
                activity.meta["changed_data"] = list(
                    set(changed_fields).union(activity.meta["changed_data"])
                )
                activity.timestamp = timezone.now()
                activity.save()
            else:
                Activity.objects.create(
                    type=Activity.TYPE_EVENT_UPDATE,
                    recipient=r,
                    event=event,
                    meta={"changed_data": changed_fields},
                )

        send_event_changed_notification.delay(event.pk, changed_fields)

        # Notify participants if new event report has been created
        if has_new_report:
            notify_on_event_report.delay(event.pk)

        # Notify group members if it is organizer group has been changed
        if changed_supportgroup:
            notify_new_group_event.delay(changed_supportgroup, event.pk)
            send_new_group_event_email.delay(changed_supportgroup, event.pk)

    def update(self, instance, validated_data):
        start = validated_data.get("start_time")
        end = validated_data.get("end_time")
        tz = validated_data.get("timezone")

        if start and end and end - start > timedelta(days=7):
            raise serializers.ValidationError(
                {"endTime": "L'événement ne peut pas durer plus de 7 jours."}
            )
        if tz and start:
            validated_data.update({"start_time": replace_datetime_timezone(start, tz)})
        if tz and end:
            validated_data.update({"end_time": replace_datetime_timezone(end, tz)})

        # Assign default description and image if needed
        if not instance.description and not validated_data.get("description"):
            validated_data.update({"description": instance.subtype.default_description})
        if not instance.image and not validated_data.get("image"):
            validated_data.update({"image": instance.subtype.default_image})

        changed_data_fields = [
            field
            for field, value in validated_data.items()
            if field in NOTIFIED_CHANGES
            and hasattr(instance, field)
            and getattr(instance, field) != value
        ]
        has_new_report = not instance.report_content and validated_data.get(
            "report_content"
        )
        changed_supportgroup = None

        with transaction.atomic():
            event = super().update(instance, validated_data)

            # Update / remove organizer group if needed
            if (
                "organizerGroup" in validated_data
                and not OrganizerConfig.objects.filter(
                    event=instance, as_group=validated_data["organizerGroup"]
                ).exists()
            ):
                OrganizerConfig.objects.update_or_create(
                    person=validated_data["organizerPerson"],
                    event=instance,
                    defaults={
                        "as_group": validated_data["organizerGroup"],
                    },
                )
                # Add group to changed data if one has been specified
                if validated_data["organizerGroup"] is not None:
                    changed_supportgroup = str(validated_data["organizerGroup"].pk)

            transaction.on_commit(
                partial(
                    self.schedule_tasks,
                    event,
                    changed_data_fields,
                    changed_supportgroup,
                    has_new_report,
                )
            )
            return event

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
            "compteRenduPhoto",
            "organizerGroup",
        ]


class EventProjectDocumentSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="precision", max_length=200)
    file = serializers.FileField(source="fichier")

    def validate_file(self, value):
        ext = PurePath(value.name).suffix
        if ext.lower() not in [".pdf", ".jpg", ".jpeg", ".png", ".docx"]:
            raise serializers.ValidationError(
                detail="Format de fichier incorrect, seuls .PDF, .JPG, .PNG et .DOCX sont autorisés",
                code="formulaire_format_incorrect",
            )
        return value

    def create(self, validated_data):
        document = Document.objects.create(
            precision=self.validated_data["precision"],
            type=self.validated_data["type"],
            description=self.validated_data["description"],
        )
        VersionDocument.objects.create(
            titre="Version initiale",
            document=document,
            fichier=self.validated_data["fichier"],
        )
        return document

    def update(self, instance, validated_data):
        raise NotImplementedError(
            "Pas implémenté : il faut vérifier pouvoir vérifier si le fichier est différent de l'actuel, et seulement "
            "si c'est le cas, créer une nouvelle version du fichier."
        )

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
        source="details.documents.absent",
        default=list,
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
            uploaded_documents,
            many=True,
            context=self.context,
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


class EventReportPersonFormSerializer(serializers.ModelSerializer):
    description = serializers.SerializerMethodField(read_only=True)
    url = serializers.SerializerMethodField(read_only=True)
    submitted = serializers.SerializerMethodField(read_only=True)

    def get_description(self, obj):
        return obj.meta_description

    def get_url(self, obj):
        return front_url(
            "view_person_form",
            kwargs={"slug": obj.slug},
            query={"reported_event_id": obj.event_pk},
        )

    def get_submitted(self, obj):
        return obj.submissions.filter(data__reported_event_id=obj.event_pk).exists()

    class Meta:
        model = PersonForm
        fields = ["title", "description", "url", "submitted"]
