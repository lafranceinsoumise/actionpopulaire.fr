from rest_framework import serializers

from agir.activity.models import Activity, Announcement
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


class AnnouncementSerializer(serializers.ModelSerializer):
    customDisplay = serializers.SlugField(source="custom_display", read_only=True)
    link = serializers.HyperlinkedIdentityField(
        view_name="activity:announcement_link", read_only=True
    )
    linkLabel = serializers.CharField(source="link_label")
    startDate = serializers.DateTimeField(source="start_date", read_only=True)
    endDate = serializers.DateTimeField(source="end_date", read_only=True)
    image = serializers.SerializerMethodField(read_only=True)
    activityId = serializers.IntegerField(
        read_only=True, source="activity_id", default=None
    )

    def get_image(self, obj):
        if obj.image:
            return {
                "desktop": obj.image.desktop.url,
                "mobile": obj.image.mobile.url,
                "activity": obj.image.activity.url,
            }
        return {}

    class Meta:
        model = Announcement
        fields = [
            "id",
            "title",
            "link",
            "linkLabel",
            "content",
            "image",
            "startDate",
            "endDate",
            "priority",
            "activityId",
            "customDisplay",
        ]


class ActivitySerializer(FlexibleFieldsMixin, serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name="activity:api_activity")
    type = serializers.CharField(read_only=True)

    timestamp = serializers.DateTimeField(read_only=True)

    event = serializers.SerializerMethodField(read_only=True)
    group = serializers.SerializerMethodField(read_only=True)
    individual = PersonSerializer(fields=["displayName", "gender"], read_only=True)

    status = serializers.CharField(required=False)
    pushStatus = serializers.CharField(
        source="push_status", write_only=True, required=False
    )
    announcement = AnnouncementSerializer(read_only=True)

    def get_group(self, instance):
        if instance.supportgroup is not None:
            return {"id": instance.supportgroup.id, "name": instance.supportgroup.name}

    def get_event(self, instance):
        if instance.event is not None:
            return {
                "id": instance.event.id,
                "name": instance.event.name,
                "startTime": instance.event.start_time,
            }

    class Meta:
        model = Activity
        fields = [
            "id",
            "url",
            "type",
            "timestamp",
            "event",
            "group",
            "individual",
            "status",
            "pushStatus",
            "meta",
            "announcement",
        ]


class CustomAnnouncementSerializer(AnnouncementSerializer):
    status = serializers.SerializerMethodField(read_only=True)

    def get_status(self, obj):
        if obj.activity_id is None:
            return None
        try:
            activity = Activity.objects.get(pk=obj.activity_id)
        except Activity.DoesNotExist:
            return None
        return activity.status

    class Meta:
        model = Announcement
        fields = [*AnnouncementSerializer.Meta.fields, "status"]


class ActivityStatusUpdateRequest(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=[Activity.STATUS_DISPLAYED, Activity.STATUS_INTERACTED]
    )
    ids = serializers.ListField(child=serializers.IntegerField())
