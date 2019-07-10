from rest_framework import serializers

from agir.notifications.models import Notification


class NotificationIdsSerializer(serializers.Serializer):
    notifications = serializers.PrimaryKeyRelatedField(
        queryset=Notification.objects.all(), many=True
    )


class ParametersSerializer(serializers.Serializer):
    length = serializers.IntegerField(min_value=5, max_value=100, default=5)
    offset = serializers.IntegerField(min_value=0, default=0)
