from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from agir.events.models import Event
from agir.events.serializers import EventSerializer
from agir.groups.serializers import SupportGroupSerializer
from agir.lib.serializers import FlexibleFieldsMixin
from agir.msgs.models import SupportGroupMessage, SupportGroupMessageComment, UserReport
from agir.people.serializers import PersonSerializer


class BaseMessageSerializer(FlexibleFieldsMixin, serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    created = serializers.DateTimeField(read_only=True)
    author = PersonSerializer(read_only=True, fields=["id", "displayName"])
    text = serializers.CharField()
    image = serializers.ImageField(required=False)


class MessageCommentSerializer(BaseMessageSerializer):
    class Meta:
        model = SupportGroupMessageComment
        fields = ("id", "author", "text", "image", "created")


class LinkedEventField(serializers.RelatedField):
    queryset = Event.objects.all()

    def to_representation(self, obj):
        if obj is None:
            return None
        return EventSerializer(obj, context=self.context).data

    def to_internal_value(self, pk):
        if pk is None:
            return None
        return self.queryset.model.objects.get(pk=pk)


class SupportGroupMessageSerializer(BaseMessageSerializer):
    RECENT_COMMENT_LIMIT = 4
    LIST_FIELDS = (
        "id",
        "created",
        "author",
        "text",
        # "image",
        "linkedEvent",
        "recentComments",
        "commentCount",
    )
    DETAIL_FIELDS = (
        "id",
        "created",
        "author",
        "text",
        # "image",
        "group",
        "linkedEvent",
        "comments",
    )

    group = SupportGroupSerializer(
        read_only=True, fields=["id", "name"], source="supportgroup"
    )
    linkedEvent = LinkedEventField(
        source="linked_event", required=False, allow_null=True
    )
    recentComments = serializers.SerializerMethodField(read_only=True)
    commentCount = serializers.SerializerMethodField(read_only=True)
    comments = serializers.SerializerMethodField(read_only=True)

    def get_recentComments(self, obj):
        recent_comments = obj.comments.filter(deleted=False).order_by("-created")[
            : self.RECENT_COMMENT_LIMIT
        ]
        if recent_comments is not None:
            recent_comments = MessageCommentSerializer(
                recent_comments, context=self.context, many=True
            ).data
        return recent_comments

    def get_commentCount(self, obj):
        count = obj.comments.filter(deleted=False).count()
        if count > self.RECENT_COMMENT_LIMIT:
            return count

    def get_comments(self, obj):
        return MessageCommentSerializer(
            obj.comments.filter(deleted=False).order_by("created"),
            context=self.context,
            many=True,
        ).data

    class Meta:
        model = SupportGroupMessage
        fields = (
            "id",
            "created",
            "author",
            "text",
            "image",
            "group",
            "linkedEvent",
            "recentComments",
            "comments",
            "commentCount",
        )


class ContentTypeChoiceField(serializers.ChoiceField):
    def to_internal_value(self, data):
        app_label, model = data.split(".")
        return ContentType.objects.get_by_natural_key(app_label, model)

    def to_representation(self, value):
        return f"{value.app_label}.{value.model}"


class UserReportSerializer(serializers.ModelSerializer):
    content_type = ContentTypeChoiceField(
        choices=("msgs.supportgroupmessage", "msgs.supportgroupmessagecomment",)
    )

    def validate(self, data):
        try:
            data["content_type"].get_object_for_this_type(pk=data["object_id"])
        except data["content_type"].model_class.DoesNotExist:
            raise serializers.ValidationError("Pas d'objet pour ce type et cette clé.")

        return data

    class Meta:
        model = UserReport
        fields = ("content_type", "object_id")
