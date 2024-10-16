from django.contrib.contenttypes.models import ContentType
from django.core import validators
from django.db import transaction
from django.db.models import Exists, OuterRef
from rest_framework import serializers

from agir.events.models import Event
from agir.events.serializers import EventListSerializer
from agir.groups.models import Membership
from agir.groups.models import SupportGroup
from agir.lib.serializers import FlexibleFieldsMixin, CurrentPersonField
from agir.lib.validators import FileSizeValidator
from agir.msgs.actions import RECENT_COMMENT_LIMIT
from agir.msgs.models import (
    SupportGroupMessage,
    SupportGroupMessageComment,
    UserReport,
    MessageAttachment,
    SupportGroupMessageRecipient,
)
from agir.people.models import Person
from agir.people.serializers import PersonSerializer


class MessageAttachmentSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        label="Nom", max_length=200, required=True, allow_null=False, allow_blank=False
    )
    file = serializers.FileField(
        label="Fichier",
        allow_empty_file=False,
        allow_null=False,
        validators=[
            validators.FileExtensionValidator(MessageAttachment.ALLOWED_EXTENSIONS),
            FileSizeValidator(MessageAttachment.MAX_SIZE),
        ],
    )

    class Meta:
        model = MessageAttachment
        fields = ("id", "name", "file", "created", "modified")
        read_only_fields = ("id", "created", "modified")


class BaseMessageSerializer(FlexibleFieldsMixin, serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    created = serializers.DateTimeField(read_only=True)
    author = serializers.SerializerMethodField()
    text = serializers.CharField(
        label="Texte",
        max_length=3000,
        required=False,
        allow_blank=True,
        allow_null=False,
    )
    attachment = MessageAttachmentSerializer(
        label="Pièce-jointe", allow_null=True, required=False
    )

    def get_author(self, obj):
        if obj.author is not None:
            return PersonSerializer(
                obj.author,
                context=self.context,
                fields=["id", "displayName", "image"],
            ).data
        return {"id": None, "displayName": "Utilisateur·ice supprimé·e", "image": None}

    def validate_instance(self, instance):
        if not instance.text and not instance.attachment:
            raise serializers.ValidationError(
                {"details": "Il n'est pas possible d'envoyer un message vide."}
            )

        return instance

    def create(self, validated_data):
        with transaction.atomic():
            attachment = validated_data.pop("attachment", None)
            message = super().create(validated_data)

            if attachment:
                attachment = MessageAttachment.objects.create(**attachment)
                message.attachment = attachment
                message.save()

            return self.validate_instance(message)

    def update(self, message, validated_data):
        with transaction.atomic():
            attachment = validated_data.pop("attachment", False)
            message = super().update(message, validated_data)

            if attachment:
                attachment = MessageAttachment.objects.create(**attachment)
                message.attachment = attachment
                message.save()
            elif attachment is None and message.attachment:
                message.attachment = None
                message.save()

            message.refresh_from_db()

            return self.validate_instance(message)


class MessageCommentSerializer(BaseMessageSerializer):
    class Meta:
        model = SupportGroupMessageComment
        fields = ("id", "author", "text", "attachment", "created")


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
                "subtype",
            ],
            context=self.context,
        ).data

    def to_internal_value(self, pk):
        if pk is None:
            return None
        return self.queryset.model.objects.get(pk=pk)


class SupportGroupMessageSerializer(BaseMessageSerializer):
    LIST_FIELDS = (
        "id",
        "created",
        "author",
        "subject",
        "text",
        "group",
        "linkedEvent",
        "attachment",
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
        "attachment",
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
        if hasattr(obj, "recent_comments"):
            recent_comments = obj.recent_comments
        else:
            recent_comments = obj.comments.active().order_by("-created")[
                :RECENT_COMMENT_LIMIT
            ]

        recent_comments = MessageCommentSerializer(
            reversed(recent_comments), context=self.context, many=True
        ).data
        return recent_comments

    def get_commentCount(self, obj):
        if hasattr(obj, "comment_count"):
            count = obj.comment_count
        else:
            count = obj.comments.active().count()
        if count > RECENT_COMMENT_LIMIT:
            return count

    def validate_instance(self, instance):
        instance = super().validate_instance(instance)

        if not instance.subject:
            raise serializers.ValidationError(
                {"subject": "L'objet du message ne peut pas être vide."}
            )

        return instance

    class Meta:
        model = SupportGroupMessage
        fields = (
            "id",
            "created",
            "author",
            "subject",
            "text",
            "attachment",
            "group",
            "linkedEvent",
            "recentComments",
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
                "image": (
                    person.image.thumbnail.url
                    if (person.image and person.image.thumbnail)
                    else None
                ),
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
    isUnread = serializers.SerializerMethodField(
        read_only=True, method_name="get_is_unread"
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
        if hasattr(message, "unread_comment_count"):
            return message.unread_comment_count
        return

    def get_is_author(self, message):
        user = self.context["request"].user
        return user.is_authenticated and user.person and message.author == user.person

    def get_is_unread(self, message):
        if hasattr(message, "last_reading_date"):
            return message.last_reading_date is None

        user = self.context["request"].user
        if user.is_authenticated and user.person:
            return SupportGroupMessageRecipient.objects.filter(
                message=message, person=user.person
            ).exists()

    def get_last_comment(self, message):
        if hasattr(message, "recent_comments"):
            comment = message.recent_comments[0] if message.recent_comments else None
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
            "attachment",
            "unreadCommentCount",
            "isAuthor",
            "lastUpdate",
            "lastComment",
            "isUnread",
            "requiredMembershipType",
        )
