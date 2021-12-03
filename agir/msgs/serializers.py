from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from agir.groups.models import SupportGroup
from agir.events.models import Event
from agir.events.serializers import EventListSerializer
from agir.lib.serializers import FlexibleFieldsMixin, CurrentPersonField
from agir.msgs.actions import get_message_unread_comment_count
from agir.msgs.models import (
    SupportGroupMessage,
    SupportGroupMessageComment,
    UserReport,
)
from agir.people.serializers import PersonSerializer
from agir.groups.models import Membership


class BaseMessageSerializer(FlexibleFieldsMixin, serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    created = serializers.DateTimeField(read_only=True)
    author = serializers.SerializerMethodField()
    text = serializers.CharField()
    image = serializers.ImageField(required=False)

    def get_author(self, obj):
        if obj.author is not None:
            return PersonSerializer(
                obj.author,
                context=self.context,
                fields=["id", "displayName", "image"],
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
        "subject",
        "text",
        "group",
        "linkedEvent",
        "recentComments",
        "commentCount",
        "requiredMembershipType",
    )
    DETAIL_FIELDS = (
        "id",
        "created",
        "author",
        "subject",
        "text",
        "group",
        "linkedEvent",
        "lastUpdate",
        "comments",
        "requiredMembershipType",
    )

    lastUpdate = serializers.DateTimeField(read_only=True, source="last_update")
    group = serializers.SerializerMethodField(read_only=True)
    linkedEvent = LinkedEventField(
        source="linked_event",
        required=False,
        allow_null=True,
    )
    recentComments = serializers.SerializerMethodField(read_only=True)
    commentCount = serializers.SerializerMethodField(read_only=True)
    comments = serializers.SerializerMethodField(read_only=True)

    requiredMembershipType = serializers.ChoiceField(
        source="required_membership_type",
        required=False,
        allow_null=True,
        choices=Membership.MEMBERSHIP_TYPE_CHOICES,
        default=Membership.MEMBERSHIP_TYPE_FOLLOWER,
    )

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
            "subject",
            "text",
            "image",
            "group",
            "linkedEvent",
            "recentComments",
            "comments",
            "commentCount",
            "lastUpdate",
            "requiredMembershipType",
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
        choices=(
            "msgs.supportgroupmessage",
            "msgs.supportgroupmessagecomment",
        )
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


class UserMessageRecipientSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportGroup
        fields = (
            "id",
            "name",
        )


class UserMessagesSerializer(BaseMessageSerializer):
    group = serializers.SerializerMethodField(read_only=True)
    unreadCommentCount = serializers.SerializerMethodField(
        read_only=True, method_name="get_unread_comment_count"
    )
    isAuthor = serializers.SerializerMethodField(
        read_only=True, method_name="get_is_author"
    )
    lastUpdate = serializers.DateTimeField(
        source="last_update", default=None, read_only=True
    )
    isUnread = serializers.BooleanField(
        source="is_unread", default=False, read_only=True
    )
    lastComment = serializers.SerializerMethodField(
        method_name="get_last_comment", read_only=True
    )

    requiredMembershipType = serializers.ChoiceField(
        source="required_membership_type",
        required=False,
        allow_null=True,
        read_only=True,
        choices=Membership.MEMBERSHIP_TYPE_CHOICES,
        default=Membership.MEMBERSHIP_TYPE_FOLLOWER,
    )

    def get_group(self, message):
        return {
            "id": message.supportgroup.id,
            "name": message.supportgroup.name,
            "referents": [
                {
                    "id": referent.id,
                    "email": referent.email,
                    "displayName": referent.display_name,
                    "gender": referent.gender,
                }
                for referent in message.supportgroup.referents
            ],
        }

    def get_unread_comment_count(self, message):
        user = self.context["request"].user
        if not user.is_authenticated or not user.person:
            return 0
        return get_message_unread_comment_count(user.person.pk, message.pk)

    def get_is_author(self, message):
        user = self.context["request"].user
        return user.is_authenticated and user.person and message.author == user.person

    def get_last_comment(self, message):
        if message.comments.exists():
            comment = message.comments.order_by("-created").first()
            return MessageCommentSerializer(comment, context=self.context).data

    class Meta:
        model = SupportGroupMessage
        fields = (
            "id",
            "created",
            "author",
            "subject",
            "text",
            "group",
            "unreadCommentCount",
            "isAuthor",
            "lastUpdate",
            "lastComment",
            "isUnread",
            "requiredMembershipType",
        )
