from django.contrib import messages
from django.middleware.csrf import get_token
from rest_framework import serializers

from agir.activity.actions import (
    get_activity,
    get_required_action_activity,
    get_announcements,
)
from agir.activity.serializers import ActivitySerializer, AnnouncementSerializer


class UserContextSerializer(serializers.Serializer):
    id = serializers.UUIDField(source="pk")
    firstName = serializers.CharField(source="first_name")
    displayName = serializers.SerializerMethodField(method_name="get_full_name")
    isInsoumise = serializers.BooleanField(source="is_insoumise")
    is2022 = serializers.BooleanField(source="is_2022")
    isAgir = serializers.BooleanField(source="is_agir")
    groups = serializers.PrimaryKeyRelatedField(
        many=True, source="supportgroups", read_only=True
    )

    def get_full_name(self, obj):
        return obj.get_full_name()


class SessionSerializer(serializers.Serializer):
    csrfToken = serializers.SerializerMethodField(method_name="get_csrf_token")
    user = serializers.SerializerMethodField(method_name="get_user")
    toasts = serializers.SerializerMethodField(method_name="get_toasts")
    activities = serializers.SerializerMethodField(method_name="get_activities")
    requiredActionActivities = serializers.SerializerMethodField(
        method_name="get_required_action_activities"
    )
    announcements = serializers.SerializerMethodField(method_name="get_announcements")

    def get_csrf_token(self, request):
        return get_token(request)

    def get_toasts(self, request):
        return [
            {"message": m.message, "html": True, "type": m.level_tag.upper()}
            for m in messages.get_messages(request)
        ]

    def get_user(self, request):
        if request.user.is_authenticated and request.user.person is not None:
            return UserContextSerializer(instance=request.user.person).data
        return False

    def get_activities(self, request):
        if request.user.is_authenticated and request.user.person is not None:
            return ActivitySerializer(
                many=True,
                instance=get_activity(request.user.person),
                context={"request": request},
            ).data

    def get_required_action_activities(self, request):
        if request.user.is_authenticated and request.user.person is not None:
            return ActivitySerializer(
                many=True,
                instance=get_required_action_activity(request.user.person),
                context={"request": request},
            ).data

    def get_announcements(self, request):
        if request.user.is_authenticated and request.user.person is not None:
            return AnnouncementSerializer(
                many=True,
                instance=get_announcements(request.user.person),
                context={"request": request},
            ).data
