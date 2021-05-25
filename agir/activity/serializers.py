from rest_framework import serializers

from agir.activity.models import Activity, Announcement
from agir.events.serializers import EventListSerializer
from agir.groups.serializers import SupportGroupSerializer
from agir.lib.serializers import FlexibleFieldsMixin
from agir.people.serializers import PersonSerializer


class ActivitySupportGroupSerializer(SupportGroupSerializer):
    def to_representation(self, instance):
        # Override SupportGroupSerializer to_representation method
        # to avoid retrieving the user membership status not in use here
        return serializers.Serializer.to_representation(self, instance)

    class Meta:
        fields = ["id", "name", "url", "routes"]


class ActivitySerializer(FlexibleFieldsMixin, serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name="activity:api_activity")
    type = serializers.CharField(read_only=True)

    timestamp = serializers.DateTimeField(read_only=True)

    event = EventListSerializer(
        fields=[
            "id",
            "name",
            "startTime",
            "endTime",
            "illustration",
            "schedule",
            "location",
            "rsvp",
            "routes",
            "subtype",
        ],
        read_only=True,
    )
    supportGroup = ActivitySupportGroupSerializer(
        source="supportgroup", fields=["id", "name", "url", "routes"], read_only=True
    )
    individual = PersonSerializer(fields=["displayName", "gender"], read_only=True)

    status = serializers.CharField()

    class Meta:
        model = Activity
        fields = [
            "id",
            "url",
            "type",
            "timestamp",
            "event",
            "supportGroup",
            "individual",
            "status",
            "meta",
        ]


class AnnouncementSerializer(serializers.ModelSerializer):
    # activityId = serializers.SerializerMethodField(read_only=True)
    customDisplay = serializers.SlugField(source="custom_display", read_only=True)
    link = serializers.HyperlinkedIdentityField(
        view_name="activity:announcement_link", read_only=True
    )
    startDate = serializers.DateTimeField(source="start_date", read_only=True)
    endDate = serializers.DateTimeField(source="end_date", read_only=True)
    image = serializers.SerializerMethodField(read_only=True)
    activityId = serializers.IntegerField(
        source="activity_id", default=None, read_only=True
    )

    def get_image(self, obj):
        if obj.image:
            return {"desktop": obj.image.desktop.url, "mobile": obj.image.mobile.url}
        return {}

    class Meta:
        model = Announcement
        fields = [
            "id",
            "title",
            "link",
            "content",
            "image",
            "startDate",
            "endDate",
            "priority",
            "activityId",
            "customDisplay",
        ]


class ActivityStatusUpdateRequest(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=[Activity.STATUS_DISPLAYED, Activity.STATUS_INTERACTED]
    )
    ids = serializers.ListField(child=serializers.IntegerField())
