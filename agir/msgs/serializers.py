from rest_framework import serializers

from agir.events.serializers import EventSerializer
from agir.groups.serializers import SupportGroupSerializer
from agir.lib.serializers import FlexibleFieldsMixin
from agir.msgs.models import SupportGroupMessage
from agir.people.serializers import PersonSerializer


class BaseMessageSerializer(FlexibleFieldsMixin, serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = PersonSerializer(read_only=True, fields=["displayName"])
    text = serializers.CharField()
    image = serializers.ImageField(required=False)


class MessageCommentSerializer(BaseMessageSerializer):
    pass


class SupportGroupMessageSerializer(BaseMessageSerializer):
    supportgroup = SupportGroupSerializer(read_only=True, fields=["id", "name"])

    class Meta:
        model = SupportGroupMessage
        fields = ("id", "author", "text", "image", "supportgroup")
