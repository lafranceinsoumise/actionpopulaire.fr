import uuid

from django.contrib import messages
from django.db.models import F
from django.middleware.csrf import get_token
from django.urls import reverse
from rest_framework import serializers

from agir.activity.actions import get_announcements
from agir.activity.models import Activity
from agir.activity.serializers import AnnouncementSerializer
from agir.authentication.utils import (
    is_hard_logged,
    is_soft_logged,
    get_bookmarked_emails,
)
from agir.groups.models import SupportGroup
from agir.lib.utils import front_url


class UserContextSerializer(serializers.Serializer):
    id = serializers.UUIDField(source="pk")
    firstName = serializers.CharField(source="first_name")
    displayName = serializers.CharField(source="display_name")
    email = serializers.CharField()
    image = serializers.SerializerMethodField()
    fullName = serializers.SerializerMethodField(method_name="get_full_name")
    isInsoumise = serializers.BooleanField(source="is_insoumise")
    is2022 = serializers.BooleanField(source="is_2022")
    isAgir = serializers.BooleanField(source="is_agir")
    groups = serializers.PrimaryKeyRelatedField(
        many=True, source="supportgroups", read_only=True
    )

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_image(self, obj):
        if obj.image and obj.image.thumbnail:
            return obj.image.thumbnail.url


class SessionSerializer(serializers.Serializer):
    csrfToken = serializers.SerializerMethodField(
        method_name="get_csrf_token", read_only=True
    )
    user = serializers.SerializerMethodField(method_name="get_user", read_only=True)
    toasts = serializers.SerializerMethodField(method_name="get_toasts", read_only=True)
    routes = serializers.SerializerMethodField(
        method_name="get_user_routes", read_only=True
    )
    facebookLogin = serializers.SerializerMethodField(
        method_name="get_facebook_login", read_only=True
    )
    hasUnreadActivities = serializers.SerializerMethodField(
        method_name="get_has_unread_activities", read_only=True
    )
    requiredActionActivitiesCount = serializers.SerializerMethodField(
        method_name="get_required_action_activities_count", read_only=True
    )
    authentication = serializers.SerializerMethodField(read_only=True)
    bookmarkedEmails = serializers.SerializerMethodField(
        method_name="get_bookmarked_emails", read_only=True
    )

    def get_authentication(self, request):
        if is_hard_logged(request):
            return 2
        if is_soft_logged(request):
            return 1
        return 0

    def get_user_routes(self, request):
        routes = {
            "search": reverse("dashboard_search"),
            "signup": reverse("signup"),
            "login": reverse("short_code_login"),
            "help": "https://infos.actionpopulaire.fr",
            "logout": reverse("disconnect"),
            "personalInformation": reverse("personal_information"),
            "nspReferral": front_url("nsp_referral"),
        }

        if request.user.is_authenticated and request.user.person is not None:
            person = request.user.person
            routes.update(
                {
                    "notificationSettings": reverse(
                        "list_activities.notification_settings"
                    )
                }
            )
            if person.is_insoumise:
                routes.update(
                    {
                        "materiel": "https://materiel.lafranceinsoumise.fr/",
                        "resources": "https://lafranceinsoumise.fr/fiches_pour_agir/",
                        "news": "https://lafranceinsoumise.fr/actualites/",
                        "thematicTeams": front_url("thematic_teams_list"),
                    }
                )
            else:
                routes.update(
                    {
                        "materiel": "https://noussommespour.fr/boutique/",
                        "resources": "https://noussommespour.fr/sinformer/",
                        "donations": "https://noussommespour.fr/don/",
                    }
                )

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
            {
                "toastId": uuid.uuid4(),
                "message": m.message,
                "html": True,
                "type": m.level_tag.upper(),
            }
            for m in messages.get_messages(request)
        ]

    def get_user(self, request):
        if request.user.is_authenticated and request.user.person is not None:
            return UserContextSerializer(instance=request.user.person).data
        return False

    def get_facebook_login(self, request):
        return (
            request.user.is_authenticated
            and request.user.social_auth.filter(provider="facebook").exists()
        )

    def get_has_unread_activities(self, request):
        if request.user.is_authenticated and request.user.person is not None:
            return (
                Activity.objects.without_required_action()
                .filter(
                    recipient=request.user.person, status=Activity.STATUS_UNDISPLAYED
                )
                .exists()
            )

    def get_required_action_activities_count(self, request):
        if request.user.is_authenticated and request.user.person is not None:
            return (
                Activity.objects.with_required_action()
                .filter(recipient=request.user.person)
                .exclude(status=Activity.STATUS_INTERACTED)
                .distinct()
                .count()
            )

    def get_bookmarked_emails(self, request):
        return get_bookmarked_emails(request)
