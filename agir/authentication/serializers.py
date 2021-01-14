from django.contrib import messages
from django.db.models import F
from django.middleware.csrf import get_token
from django.urls import reverse
from rest_framework import serializers

from agir.activity.actions import (
    get_activities,
    get_required_action_activities,
    get_announcements,
)
from agir.activity.serializers import ActivitySerializer, AnnouncementSerializer
from agir.groups.models import SupportGroup
from agir.lib.utils import front_url


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
    routes = serializers.SerializerMethodField(method_name="get_user_routes")

    def get_user_routes(self, request):
        if request.user.is_authenticated:
            person = request.user.person

            if person.is_insoumise:
                routes = {
                    "materiel": "https://materiel.lafranceinsoumise.fr/",
                    "resources": "https://lafranceinsoumise.fr/fiches_pour_agir/",
                    "news": "https://lafranceinsoumise.fr/actualites/",
                    "thematicTeams": front_url("thematic_teams_list"),
                    "nspReferral": front_url("nsp_referral"),
                }
            else:
                routes = {
                    "materiel": "https://noussommespour.fr/boutique/",
                    "resources": "https://noussommespour.fr/sinformer/",
                    "donations": "https://noussommespour.fr/don/",
                    "nspReferral": front_url("nsp_referral"),
                }

            person_groups = (
                SupportGroup.objects.filter(memberships__person=person)
                .active()
                .annotate(membership_type=F("memberships__membership_type"))
                .order_by("-membership_type", "name")
            )

            if person_groups.count() > 0:
                routes["groups__personGroups"] = []
                for group in person_groups:
                    link = {
                        "id": group.id,
                        "label": group.name,
                        "to": reverse("view_group", kwargs={"pk": group.pk}),
                    }
                    routes["groups__personGroups"].append(link)

            return routes

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
                instance=get_activities(request.user.person),
                context={"request": request},
            ).data

    def get_required_action_activities(self, request):
        if request.user.is_authenticated and request.user.person is not None:
            return ActivitySerializer(
                many=True,
                instance=get_required_action_activities(request.user.person),
                context={"request": request},
            ).data

    def get_announcements(self, request):
        if request.user.is_authenticated and request.user.person is not None:
            return AnnouncementSerializer(
                many=True,
                instance=get_announcements(request.user.person),
                context={"request": request},
            ).data
