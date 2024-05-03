import datetime
from datetime import timedelta
from functools import partial
from pathlib import PurePath

from dateutil.relativedelta import relativedelta
from django.db import transaction
from django.db.models import Value, Func, Q
from django.db.models.functions import Concat, Replace, Lower, MD5
from django.utils import timezone
from django.utils.text import slugify
from django_countries.serializer_fields import CountryField
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
from ..lib.display import display_liststring

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


class DisplayEventSubtypeSerializer(serializers.ModelSerializer):
    iconName = serializers.SerializerMethodField(read_only=True)
    icon = serializers.SerializerMethodField(read_only=True)
    color = serializers.SerializerMethodField(read_only=True)

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
            "emoji",
            "icon",
            "iconName",
            "type",
        )


class EventSubtypeSerializer(DisplayEventSubtypeSerializer):
    needsDocuments = serializers.SerializerMethodField(read_only=True)
    isVisible = serializers.SerializerMethodField(read_only=True)
    isPrivate = serializers.BooleanField(
        source="for_organizer_group_members_only", read_only=True
    )
    forGroupType = serializers.CharField(
        read_only=True, source="get_for_supportgroup_type_display"
    )
    forGroups = serializers.SerializerMethodField(
        read_only=True, method_name="get_for_supportgroups"
    )

    def get_needsDocuments(self, obj):
        return bool(obj.related_project_type)

    def get_isVisible(self, obj):
        return obj.visibility == EventSubtype.VISIBILITY_ALL

    def get_for_supportgroups(self, obj):
        return list(obj.for_supportgroups.values("id", "name"))

    class Meta:
        model = models.EventSubtype
        fields = (
            "id",
            "label",
            "description",
            "color",
            "emoji",
            "icon",
            "iconName",
            "type",
            "needsDocuments",
            "isVisible",
            "isPrivate",
            "forGroupType",
            "forGroups",
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
        "distance",
        "eventSpeakers",
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
    rsvped = serializers.SerializerMethodField(read_only=True)
    canRSVP = serializers.SerializerMethodField(method_name="can_rsvp", read_only=True)
    canCancelRSVP = serializers.SerializerMethodField(
        method_name="can_cancel_rsvp", read_only=True
    )
    canRSVPAsGroup = serializers.SerializerMethodField(
        method_name="can_rsvp_as_group", read_only=True
    )
    options = EventOptionsSerializer(source="*")
    routes = RoutesField(routes=EVENT_ROUTES)
    groups = serializers.SerializerMethodField()
    groupsAttendees = serializers.SerializerMethodField(
        method_name="get_groups_attendees"
    )
    contact = serializers.SerializerMethodField()
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
    unauthorizedMessage = serializers.CharField(
        source="subtype.unauthorized_message", read_only=True
    )
    eventSpeakers = serializers.SerializerMethodField(
        method_name="get_event_speakers", read_only=True
    )
    volunteerApplicationFormLink = serializers.URLField(
        source="volunteer_application_form.front_url", read_only=True
    )
    hasProject = serializers.SerializerMethodField(
        read_only=True, method_name="get_has_project"
    )

    def __init__(self, instance=None, data=empty, fields=None, **kwargs):
        self.is_event_card = fields == self.EVENT_CARD_FIELDS
        self.person = None
        super().__init__(instance=instance, data=data, fields=fields, **kwargs)

    def to_representation(self, instance):
        if not self.context.get("request", None):
            return super().to_representation(instance)

        user = self.context["request"].user
        if (
            not user.is_anonymous
            and hasattr(user, "person")
            and user.person is not None
        ):
            self.person = user.person

        if not self.is_event_card and self.person:
            # this allow prefetching by queryset annotation for performances
            if not hasattr(instance, "_pf_person_organizer_configs"):
                self.organizer_config = OrganizerConfig.objects.filter(
                    event=instance, person=self.person
                ).first()
            else:
                self.organizer_config = (
                    instance._pf_person_organizer_configs[0]
                    if len(instance._pf_person_organizer_configs)
                    else None
                )
            if not hasattr(instance, "_pf_person_rsvps"):
                self.rsvp = (
                    RSVP.objects.filter(event=instance, person=self.person)
                    .order_by("-created")
                    .first()
                )
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
        if not self.person:
            return False

        if bool(self.organizer_config):
            return True

        if obj.organizers_groups.filter(
            memberships__person=self.person,
            memberships__membership_type__gte=Membership.MEMBERSHIP_TYPE_REFERENT,
        ).exists():
            return True

        return False

    def get_isManager(self, obj):
        if not self.person:
            return False

        if bool(self.organizer_config):
            return True

        if obj.organizers_groups.filter(
            memberships__person=self.person,
            memberships__membership_type__gte=Membership.MEMBERSHIP_TYPE_MANAGER,
        ).exists():
            return True

        return False

    def get_rsvp(self, _obj):
        return self.rsvp and self.rsvp.status

    def get_rsvped(self, _obj):
        return self.rsvp and self.rsvp.status == RSVP.Status.CONFIRMED

    def can_rsvp(self, obj):
        return obj.can_rsvp(self.person)

    def can_cancel_rsvp(self, obj):
        return obj.can_cancel_rsvp(self.person)

    def can_rsvp_as_group(self, obj):
        return obj.can_rsvp_as_group(self.person)

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

    def get_contact(self, obj):
        # Hide contact information one week after the event end
        if timezone.now() > obj.end_time + timedelta(days=7):
            return None
        return ContactMixinSerializer(
            source="*", context=self.context
        ).to_representation(obj)

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
        if self.is_event_card:
            if hasattr(obj, "_pf_organizer_groups"):
                return [
                    {"id": group.id, "name": group.name}
                    for group in obj._pf_organizer_groups
                ]
            return list(obj.organizers_groups.distinct().values("id", "name"))

        return SupportGroupSerializer(
            (
                obj.organizers_groups.distinct()
                .with_organized_event_count()
                .with_membership_count()
                .with_person_membership(person=self.person)
            ),
            context=self.context,
            many=True,
            fields=[
                "id",
                "name",
                "eventCount",
                "membersCount",
                "isMember",
                "isManager",
            ],
        ).data

    def get_groups_attendees(self, obj):
        if hasattr(obj, "_pf_group_attendees"):
            groups = [
                {"id": group.id, "name": group.name}
                for group in obj._pf_group_attendees
            ]
        else:
            groups = list(obj.groups_attendees.distinct().values("id", "name"))

        if self.is_event_card:
            return groups

        if not self.person:
            return [{**group, "isManager": False} for group in groups]

        managed_group_ids = (
            self.person.memberships.managers()
            .filter(
                supportgroup_id__in=[group["id"] for group in groups],
            )
            .values_list("supportgroup_id", flat=True)
        )

        return [
            {**group, "isManager": group["id"] in managed_group_ids} for group in groups
        ]

    def get_is_past(self, obj):
        return obj.is_past()

    def get_has_project(self, obj):
        return (
            Projet.objects.exclude(etat__in=Projet.ETATS_FINAUX)
            .filter(event=obj)
            .exists()
        )

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

    def get_event_speakers(self, obj):
        event_speakers = list(obj.event_speakers.all())
        return [
            {
                "id": event_speaker.id,
                "name": event_speaker.person.get_full_name(),
                "image": (
                    event_speaker.person.image.thumbnail.url
                    if event_speaker.person.image
                    else None
                ),
                "description": event_speaker.description,
            }
            for event_speaker in event_speakers
        ]


class EventAdvancedSerializer(EventSerializer):
    participants = serializers.SerializerMethodField()
    contact = NestedContactSerializer(source="*")
    groupsInvited = serializers.SerializerMethodField(method_name="get_groups_invited")
    isCoorganizable = serializers.BooleanField(
        source="subtype.is_coorganizable", read_only=True
    )

    def format_person(
        self, person, is_speaker=False, is_organizer=False, unavailable=False
    ):
        formatted_person = {
            "id": person.id,
            "displayName": person.display_name,
            "image": None,
            "isOrganizer": is_organizer,
            "isEventSpeaker": is_speaker,
            "unavailable": unavailable,
        }

        if person.image and person.image.thumbnail:
            formatted_person["image"] = person.image.thumbnail.url

        if is_speaker:
            formatted_person["displayName"] = person.get_full_name()

        if unavailable and not is_organizer:
            return formatted_person

        return {
            **formatted_person,
            "email": person.display_email,
            "gender": person.gender,
        }

    def get_participants(self, obj):
        speaker_person_ids = list(
            obj.event_speakers.values_list("person_id", flat=True)
        )
        organizers = {
            str(person.id): self.format_person(
                person, is_organizer=True, is_speaker=person.id in speaker_person_ids
            )
            for person in obj.get_organizer_people()
        }
        participants = {
            str(person.id): self.format_person(
                person,
                is_organizer=str(person.id) in organizers.keys(),
                is_speaker=person.id in speaker_person_ids,
                unavailable=person.unavailable,
            )
            for person in obj.annotated_attendees
            if person.confirmed or person.unavailable
        }
        participants = {
            **organizers,
            **participants,
        }

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
    lastUsedSubtypeIds = serializers.SerializerMethodField(
        method_name="get_last_used_subtype_ids"
    )
    defaultContact = serializers.SerializerMethodField()
    recentLocations = serializers.SerializerMethodField(
        method_name="get_recent_locations"
    )
    # onlineUrl = serializers.SerializerMethodField()

    def to_representation(self, instance):
        if not self.context.get("request", None):
            return super().to_representation(instance)

        user = self.context["request"].user
        self.person = None
        self.managed_groups = []
        if not user.is_anonymous and user.person:
            self.person = user.person
            self.managed_groups = list(
                SupportGroup.objects.with_static_map_image()
                .filter(
                    memberships__person_id=self.person.id,
                    memberships__membership_type__gte=Membership.MEMBERSHIP_TYPE_MANAGER,
                )
                .active()
            )
        return super().to_representation(instance)

    def get_organizerGroup(self, _request):
        return SupportGroupDetailSerializer(
            self.managed_groups,
            context=self.context,
            many=True,
            fields=["id", "name", "contact", "location", "isCertified"],
        ).data

    def get_subtype(self, _request):
        subtypes = EventSubtype.objects.prefetch_related("for_supportgroups").filter(
            visibility=EventSubtype.VISIBILITY_ALL
        )
        if self.managed_groups:
            subtypes = subtypes.filter(
                Q(for_supportgroup_type__isnull=True)
                | Q(
                    for_supportgroup_type__in=[
                        group.type for group in self.managed_groups
                    ]
                )
            ).filter(
                Q(for_supportgroups__isnull=True)
                | Q(for_supportgroups__in=self.managed_groups)
            )
        else:
            subtypes = subtypes.filter(
                for_supportgroup_type__isnull=True, for_supportgroups__isnull=True
            )

        subtypes = subtypes.order_by("-has_priority", "description")

        return EventSubtypeSerializer(
            subtypes,
            context=self.context,
            many=True,
        ).data

    def get_last_used_subtype_ids(self, _request):
        return (
            Event.objects.exclude(visibility=Event.VISIBILITY_ADMIN)
            .filter(subtype__visibility=EventSubtype.VISIBILITY_ALL)
            .filter(organizers=self.person)
            .order_by("subtype_id", "-start_time")
            .distinct("subtype_id")
            .values_list("subtype_id", flat=True)[:5]
        )

    def get_defaultContact(self, _request):
        contact = {
            "hidePhone": False,
        }
        if self.person and self.person.display_name:
            contact["name"] = self.person.display_name
        if self.person and self.person.contact_phone:
            contact["phone"] = str(self.person.contact_phone)
        if self.person and self.person.display_email:
            contact["email"] = self.person.display_email
        return contact

    def get_onlineUrl(self, _request):
        return "https://" + jitsi_default_domain() + "/" + jitsi_default_room_name()

    def get_recent_locations(self, _request):
        if not self.person:
            return []

        recent_distinct_location_event_ids = [
            event["pk"]
            for event in (
                self.person.organized_events.public()
                .filter(
                    coordinates__isnull=False, coordinates_type=Event.COORDINATES_EXACT
                )
                .filter(created__gte=timezone.now() - relativedelta(years=+1))
                .annotate(
                    location_hash=MD5(
                        Func(
                            Replace(
                                Lower(
                                    Concat(
                                        "location_address1",
                                        "location_zip",
                                    )
                                ),
                                Value(" "),
                                Value(""),
                            ),
                            function="unaccent",
                        )
                    )
                )
                .distinct("location_hash")
                .order_by("location_hash")
                .values("pk", "location_hash")
            )
        ]

        if not recent_distinct_location_event_ids:
            return []

        recent_locations = (
            Event.objects.filter(pk__in=recent_distinct_location_event_ids)
            .values(
                "id",
                "location_name",
                "location_address1",
                "location_address2",
                "location_zip",
                "location_city",
                "location_country",
            )
            .order_by("-created")[:4]
        )

        return [
            {
                key.replace("location_", ""): value
                for key, value in recent_location.items()
            }
            for recent_location in recent_locations
        ]


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
        source="online_url", required=False, allow_blank=True, max_length=2000
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
        organizer = data.get("organizerPerson", None)
        organizer_group = data.get("organizerGroup", None)

        if organizer_group and organizer not in organizer_group.managers:
            raise serializers.ValidationError(
                {
                    "organizerGroup": "Veuillez choisir un groupe dont vous êtes animateur·ice"
                }
            )

        if data["subtype"].for_organizer_group_members_only and not organizer_group:
            raise serializers.ValidationError(
                {
                    "organizerGroup": "Ce type d'événement ne peut pas être organisé à titre individuel"
                }
            )

        if data["subtype"].for_supportgroup_type and not organizer_group:
            raise serializers.ValidationError(
                {
                    "organizerGroup": "Ce type d'événement ne peut pas être organisé à titre individuel"
                }
            )

        if (
            data["subtype"].for_supportgroup_type
            and organizer_group.type != data["subtype"].for_supportgroup_type
        ):
            raise serializers.ValidationError(
                {
                    "organizerGroup": f"Ce type d'événement peut être organisé uniquement "
                    f"par des groupes du type « {data['subtype'].get_for_supportgroup_type_display()} »"
                }
            )

        for_supportgroups = list(data["subtype"].for_supportgroups.all())
        if for_supportgroups and not organizer_group:
            raise serializers.ValidationError(
                {
                    "organizerGroup": "Ce type d'événement ne peut pas être organisé à titre individuel"
                }
            )

        if for_supportgroups and organizer_group not in for_supportgroups:
            raise serializers.ValidationError(
                {
                    "organizerGroup": "Ce type d'événement ne peut pas être organisé par le groupe sélectionné"
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

        # Create a gestion project if needed for the event's subtype
        if event.subtype.related_project_type:
            Projet.objects.from_event(event, event.organizers.first().role)

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
    onlineUrl = serializers.URLField(
        source="online_url", allow_blank=True, max_length=2000
    )
    facebook = serializers.CharField(allow_blank=True, max_length=255)
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
        for r in event.confirmed_attendees:
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

                if (
                    Projet.objects.exclude(etat__in=Projet.ETATS_FINAUX)
                    .filter(event=event)
                    .exists()
                ):
                    Projet.objects.from_event(event, event.organizers.first().role)

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


class EventEmailCampaignSerializer(serializers.ModelSerializer):
    FIELD_FORMATTING = (
        ("datetime", "capitalize"),
        ("simple_datetime", "capitalize"),
        ("location_name", "title"),
        ("location_city", "title"),
    )

    campaign_message_subject = serializers.CharField(default="")
    campaign_name = serializers.SerializerMethodField()
    campaign_utm_name = serializers.SerializerMethodField()
    campaign_start_date = serializers.SerializerMethodField()
    campaign_end_date = serializers.SerializerMethodField()

    theme = serializers.CharField(source="meta.event_theme", default="")
    theme_type = serializers.CharField(source="meta.event_theme_type", default="")
    image = serializers.URLField(source="get_absolute_image_url", default="")
    page_url = serializers.URLField(source="get_absolute_url", default="")
    facebook_url = serializers.URLField(source="facebook", default="")
    date = serializers.CharField(source="get_datestring")
    location_country = CountryField(name_only=True)

    time = serializers.SerializerMethodField()
    datetime = serializers.SerializerMethodField()
    simple_datetime = serializers.SerializerMethodField()
    speaker_names = serializers.SerializerMethodField()
    speaker_list = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_speakers = []
        if self.instance:
            self.event_speakers = list(
                self.instance.event_speakers.select_related("person").all()
            )

    def get_speaker_names(self, _event):
        return display_liststring(
            [s.person.get_full_name().title() for s in self.event_speakers]
        )

    def get_speaker_list(self, _event):
        return display_liststring([s.get_title() for s in self.event_speakers])

    def get_campaign_name(self, event):
        return str(event)

    def get_campaign_utm_name(self, event):
        return slugify(str(event))

    def get_campaign_start_date(self, event):
        return event.start_time - datetime.timedelta(days=7)

    def get_campaign_end_date(self, event):
        return event.start_time

    def get_time(self, event):
        return event.get_timestring(hide_default_tz=True)

    def get_datetime(self, event):
        return event.get_display_date(hide_default_tz=True)

    def get_simple_datetime(self, event):
        return event.get_simple_display_date(hide_default_tz=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        for field, format_fn in self.FIELD_FORMATTING:
            value = data[field]
            if value and hasattr(value, format_fn):
                if callable(getattr(value, format_fn)):
                    data[field] = getattr(value, format_fn)()
                else:
                    data[field] = getattr(value, format_fn)

        if template := instance.subtype.campaign_template:
            data["campaign_message_subject"] = template.message_subject
            for field in data:
                substitute = str(data[field]).replace("{", "")
                data["campaign_message_subject"] = data[
                    "campaign_message_subject"
                ].replace(f"[{field}]", substitute)

        return data

    class Meta:
        model = Event
        fields = read_only_fields = (
            "campaign_name",
            "campaign_utm_name",
            "campaign_start_date",
            "campaign_end_date",
            "campaign_message_subject",
            "name",
            "theme",
            "theme_type",
            "image",
            "page_url",
            "facebook_url",
            "date",
            "time",
            "datetime",
            "simple_datetime",
            "location_name",
            "location_address1",
            "location_address2",
            "location_zip",
            "location_city",
            "location_country",
            "speaker_names",
            "speaker_list",
        )
