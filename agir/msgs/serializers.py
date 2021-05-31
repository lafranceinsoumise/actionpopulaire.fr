from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from agir.events.models import Event
from agir.events.serializers import EventListSerializer
from agir.lib.serializers import FlexibleFieldsMixin, CurrentPersonField
from agir.msgs.models import SupportGroupMessage, SupportGroupMessageComment, UserReport
from agir.people.serializers import PersonSerializer


class BaseMessageSerializer(FlexibleFieldsMixin, serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    created = serializers.DateTimeField(read_only=True)
    author = serializers.SerializerMethodField()
    text = serializers.CharField()
    image = serializers.ImageField(required=False)

    def get_author(self, obj):
        if obj.author is not None:
            return PersonSerializer(
                obj.author, context=self.context, fields=["id", "displayName", "image"],
            ).data
        return {"id": None, "displayName": "Utilisateur·ice supprimé·e", "image": None}


class MessageCommentSerializer(BaseMessageSerializer):
    class Meta:
        model = SupportGroupMessageComment
        fields = ("id", "author", "text", "image", "created")


class LinkedEventField(serializers.RelatedField):
    queryset = Event.objects.all()

    def to_representation(self, obj):
        if obj is None:
            return None
        return EventListSerializer(
            obj,
            fields=[
                "id",
                "name",
                "illustration",
                "startTime",
                "endTime",
                "location",
                "rsvp",
                "routes",
                "compteRendu",
                "subtype",
            ],
            context=self.context,
        ).data

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
        "group",
        "linkedEvent",
        "recentComments",
        "commentCount",
    )
    DETAIL_FIELDS = (
        "id",
        "created",
        "author",
        "text",
        "group",
        "linkedEvent",
        "comments",
    )

    group = serializers.SerializerMethodField(read_only=True)
    linkedEvent = LinkedEventField(
        source="linked_event", required=False, allow_null=True,
    )
    recentComments = serializers.SerializerMethodField(read_only=True)
    commentCount = serializers.SerializerMethodField(read_only=True)
    comments = serializers.SerializerMethodField(read_only=True)

    def get_group(self, obj):
        return {
            "id": obj.supportgroup.id,
            "name": obj.supportgroup.name,
        }

    def get_recentComments(self, obj):
        recent_comments = (
            obj.comments.filter(deleted=False)
            .select_related("author")
            .order_by("-created")[: self.RECENT_COMMENT_LIMIT]
        )
        if recent_comments is not None:
            recent_comments = MessageCommentSerializer(
                reversed(recent_comments), context=self.context, many=True
            ).data
        return recent_comments

    def get_commentCount(self, obj):
        count = obj.comments.filter(deleted=False).count()
        if count > self.RECENT_COMMENT_LIMIT:
            return count

    def get_comments(self, obj):
        return MessageCommentSerializer(
            obj.comments.filter(deleted=False)
            .select_related("author")
            .order_by("created"),
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
    reporter = CurrentPersonField()
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
        fields = ("reporter", "content_type", "object_id")
