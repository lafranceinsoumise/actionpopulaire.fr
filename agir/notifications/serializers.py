from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from agir.activity.models import Activity
from agir.groups.models import Membership, SupportGroup
from agir.groups.serializers import SupportGroupSerializer

from .models import Subscription


class CurrentPersonDefault:
    requires_context = True

    def __call__(self, serializer_field):
        user = serializer_field.context["request"].user
        if user.is_authenticated and user.person is not None:
            return user.person


class SubscriptionSupportGroupSerializer(SupportGroupSerializer):
    def to_internal_value(self, data):
        if data is None:
            return data
        if not isinstance(data, str):
            raise serializers.ValidationError(
                "Incorrect type. Expected a string, but got %s" % type(data).__name__
            )
        try:
            return SupportGroup.objects.get(pk=data)
        except SupportGroup.DoesNotExist:
            raise serializers.ValidationError(
                "No group found for the id %s" % str(data)
            )


class SubscriptionSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    person = serializers.UUIDField(default=CurrentPersonDefault(), write_only=True)
    type = serializers.ChoiceField(
        choices=Subscription.SUBSCRIPTION_CHOICES,
        required=True,
        allow_blank=False,
        allow_null=False,
    )
    activityType = serializers.ChoiceField(
        choices=Activity.TYPE_CHOICES,
        required=True,
        allow_blank=False,
        allow_null=False,
        source="activity_type",
    )
    group = SubscriptionSupportGroupSerializer(
        source="membership.supportgroup", default=None, allow_null=True, required=False
    )

    def validate(self, data):
        membership = data.pop("membership", None)
        data["membership"] = None
        if membership is not None and membership["supportgroup"] is not None:
            try:
                data["membership"] = Membership.objects.get(
                    supportgroup=membership["supportgroup"], person=data["person"],
                )
            except Membership.DoesNotExist:
                raise serializers.ValidationError({"group": "Invalid group"})

        return data

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError:
            raise serializers.ValidationError({"global": "IntegrityError message"})

    class Meta:
        model = Subscription
        fields = ("id", "person", "type", "activityType", "group")
