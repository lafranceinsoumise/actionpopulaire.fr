from django_countries.serializers import CountryFieldMixin
from rest_framework import serializers

from agir.lib.serializers import (
    ExistingRelatedLabelField,
    LocationSerializer,
    ContactMixinSerializer,
)
from agir.front.serializer_utils import MediaURLField, RoutesField
from . import models
from .models import OrganizerConfig, RSVP
from ..groups.serializers import SupportGroupReactSerializer


class EventSerializer(CountryFieldMixin, serializers.ModelSerializer):
    subtype = ExistingRelatedLabelField(
        queryset=models.EventSubtype.objects.all(), required=False
    )

    class Meta:
        model = models.Event
        fields = (
            "id",
            "name",
            "description",
            "start_time",
            "end_time",
            "contact_name",
            "contact_email",
            "location_address1",
            "location_address2",
            "location_city",
            "location_zip",
            "location_country",
            "coordinates",
            "subtype",
        )


class EventSubtypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EventSubtype
        fields = ("label", "description", "color", "icon", "type")


EVENT_ROUTES = {
    "page": "view_event",
    "map": "carte:single_event_map",
    "attend": "rsvp_event",
    "cancel": "quit_event",
    "manage": "manage_event",
    "calendarExport": "ics_event",
    "compteRendu": "edit_event_report",
    "addPhoto": "upload_event_image",
}


class EventOptionsSerializer(serializers.Serializer):
    price = serializers.SerializerMethodField()

    def get_price(self, obj):
        return obj.get_price_display()


class EventReactSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    url = serializers.HyperlinkedIdentityField(view_name="view_event")
    name = serializers.CharField()
    hasSubscriptionForm = serializers.SerializerMethodField()

    description = serializers.CharField()
    compteRendu = serializers.CharField(source="report_content")
    compteRenduPhotos = serializers.SerializerMethodField()
    illustration = MediaURLField(source="image")

    startTime = serializers.DateTimeField(source="start_time")
    endTime = serializers.DateTimeField(source="end_time")

    location = LocationSerializer(source="*")

    isOrganizer = serializers.SerializerMethodField()
    rsvp = serializers.SerializerMethodField()
    participantCount = serializers.IntegerField(source="participants")

    options = EventOptionsSerializer(source="*")

    routes = RoutesField(routes=EVENT_ROUTES)

    groups = SupportGroupReactSerializer(many=True, source="organizers_groups")

    contact = ContactMixinSerializer(source="*")

    def to_representation(self, instance):
        user = self.context["request"].user
        self.organizer_config = self.rsvp = None

        if user.is_authenticated and user.person:
            self.organizer_config = OrganizerConfig.objects.filter(
                event=instance, person=user.person
            ).first()
            self.rsvp = RSVP.objects.filter(event=instance, person=user.person).first()

        return super().to_representation(instance)

    def get_hasSubscriptionForm(self, obj):
        return bool(obj.subscription_form_id)

    def get_isOrganizer(self, obj):
        return bool(self.organizer_config)

    def get_rsvp(self, obj):
        return self.rsvp and self.rsvp.status

    def get_compteRenduPhotos(self, obj):
        return [image.image for image in obj.images.all()]

    def get_routes(self, obj):
        routes = {}

        if obj.facebook:
            routes["facebook"] = f"https://www.facebook.com/events/{obj.facebook}"

        routes["googleExport"] = obj.get_google_calendar_url()

        return routes
