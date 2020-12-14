from rest_framework import serializers

from agir.activity.models import Activity, Announcement
from agir.events.serializers import EventSerializer
from agir.groups.serializers import SupportGroupSerializer
from agir.lib.serializers import FlexibleFieldsMixin
from agir.people.serializers import PersonSerializer


class ActivitySerializer(FlexibleFieldsMixin, serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name="activity:api_activity")
    type = serializers.CharField(read_only=True)

    timestamp = serializers.DateTimeField(read_only=True)

    event = EventSerializer(
        fields=[
            "id",
            "name",
            "startTime",
            "endTime",
            "participantCount",
            "illustration",
            "schedule",
            "location",
            "rsvp",
            "routes",
        ],
        read_only=True,
    )
    supportGroup = SupportGroupSerializer(
        source="supportgroup", fields=["name", "url"], read_only=True
    )
    individual = PersonSerializer(fields=["firstName", "email"], read_only=True)

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
    startDate = serializers.DateTimeField(source="start_date")
    endDate = serializers.DateTimeField(source="end_date")

    image = serializers.SerializerMethodField()

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
        ]
