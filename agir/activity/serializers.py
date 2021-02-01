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

    event = EventSerializer(fields=EventSerializer.EVENT_CARD_FIELDS, read_only=True,)
    supportGroup = SupportGroupSerializer(
        source="supportgroup", fields=["name", "url", "routes"], read_only=True
    )
    individual = PersonSerializer(fields=["firstName", "gender"], read_only=True)

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
    activityId = serializers.SerializerMethodField()

    link = serializers.HyperlinkedIdentityField(view_name="activity:announcement_link")

    startDate = serializers.DateTimeField(source="start_date")
    endDate = serializers.DateTimeField(source="end_date")

    image = serializers.SerializerMethodField()

    def get_activityId(self, obj):
        user = self.context["request"].user
        if getattr(obj, "activity_id", None):
            return obj.activity_id
        if hasattr(user, "person"):
            activity = Activity.objects.create(
                type=Activity.TYPE_ANNOUNCEMENT, recipient=user.person, announcement=obj
            )
            return activity.id

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
        ]


class ActivityStatusUpdateRequest(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=[Activity.STATUS_DISPLAYED, Activity.STATUS_INTERACTED]
    )
    ids = serializers.ListField(child=serializers.IntegerField())
