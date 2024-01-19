from django.contrib.contenttypes.models import ContentType
from django.db.models import Exists, OuterRef
from rest_framework import serializers

from agir.events.models import Event
from agir.events.serializers import EventListSerializer
from agir.groups.models import Membership
from agir.groups.models import SupportGroup
from agir.lib.serializers import FlexibleFieldsMixin, CurrentPersonField
from agir.msgs.actions import get_message_unread_comment_count
from agir.msgs.models import (
    SupportGroupMessage,
    SupportGroupMessageComment,
    UserReport,
)
from agir.people.models import Person
from agir.people.serializers import PersonSerializer


class BaseMessageSerializer(FlexibleFieldsMixin, serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    created = serializers.DateTimeField(read_only=True)
    author = serializers.SerializerMethodField()
    text = serializers.CharField(max_length=3000)
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
        "isLocked",
        "readonly",
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
        "requiredMembershipType",
        "isLocked",
        "readonly",
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

    requiredMembershipType = serializers.ChoiceField(
        source="required_membership_type",
        required=False,
        allow_null=True,
        choices=Membership.MEMBERSHIP_TYPE_CHOICES,
        default=Membership.MEMBERSHIP_TYPE_FOLLOWER,
    )
    isLocked = serializers.BooleanField(
        source="is_locked",
        default=False,
        allow_null=True,
        required=False,
        read_only=True,
    )
    readonly = serializers.BooleanField(
        default=False,
        allow_null=True,
        required=False,
        read_only=True,
    )

    def get_group(self, obj):
        user = self.context["request"].user.person
        is_manager = user in obj.supportgroup.managers
        return {
            "id": obj.supportgroup.id,
            "name": obj.supportgroup.name,
            "isManager": is_manager,
        }

    def get_recentComments(self, obj):
        recent_comments = (
            obj.comments.active()
            .select_related("author")
            .order_by("-created")[: self.RECENT_COMMENT_LIMIT]
        )
        if recent_comments is not None:
            recent_comments = MessageCommentSerializer(
                reversed(recent_comments), context=self.context, many=True
            ).data
        return recent_comments

    def get_commentCount(self, obj):
        count = obj.comments.active().count()
        if count > self.RECENT_COMMENT_LIMIT:
            return count

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
            "isLocked",
            "readonly",
        )


class SupportGroupMessageParticipantSerializer(serializers.ModelSerializer):
    active = serializers.SerializerMethodField(read_only=True)
    total = serializers.SerializerMethodField(read_only=True)

    def to_representation(self, message):
        recipient_ids = [message.author_id] + list(
            Membership.objects.exclude(person_id=message.author_id)
            .filter(
                supportgroup_id=message.supportgroup_id,
                membership_type__gte=message.required_membership_type,
            )
            .values_list("person_id", flat=True)
        )
        self.participants = list(
            Person.objects.filter(id__in=recipient_ids).annotate(
                has_commented=Exists(message.comments.filter(author_id=OuterRef("id")))
            )
        )
        return super().to_representation(message)

    def get_active(self, message):
        return [
            {
                "id": person.id,
                "displayName": person.display_name,
                "gender": person.gender,
                "isAuthor": message.author_id == person.id,
                "image": person.image.thumbnail.url
                if (person.image and person.image.thumbnail)
                else None,
            }
            for person in self.participants
            if person.has_commented or message.author_id == person.id
        ]

    def get_total(self, _):
        return len(self.participants)

    class Meta:
        model = SupportGroupMessage
        fields = ("active", "total")


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
    subject = serializers.SerializerMethodField(read_only=True)
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

    def get_subject(self, message):
        if message.subject:
            return message.subject

        if message.required_membership_type >= Membership.MEMBERSHIP_TYPE_MANAGER:
            participants = [message.author.display_name] + [
                person.display_name for person in message.supportgroup.referents
            ]
            if len(participants) < 3:
                return " et ".join(participants)
            return f"{', '.join(participants[:-1])} et {participants[-1]}"

        return ""

    def get_group(self, message):
        return {
            "id": message.supportgroup.id,
            "name": message.supportgroup.name,
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
        if hasattr(message, "_pf_last_comment"):
            comment = (
                message._pf_last_comment.pop() if message._pf_last_comment else None
            )
        else:
            comment = message.comments.active().order_by("-created").first()
        if comment is None:
            return
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
