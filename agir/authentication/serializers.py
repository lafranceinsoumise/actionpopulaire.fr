import uuid

from django.contrib import messages
from django.db.models import F
from django.urls import reverse
from django_countries.serializer_fields import CountryField
from rest_framework import serializers

from agir.authentication.utils import (
    is_hard_logged,
    is_soft_logged,
    get_bookmarked_emails,
)
from agir.donations.actions import (
    get_active_contribution_for_person,
    get_contribution_end_date,
    is_renewable_contribution,
)
from agir.donations.views.donations_views import DONATION_SESSION_NAMESPACE
from agir.groups.models import SupportGroup, Membership
from agir.lib.utils import front_url
from agir.people.serializers import PersonNewsletterListField
from agir.voting_proxies.models import VotingProxyRequest


class UserContextSerializer(serializers.Serializer):
    id = serializers.UUIDField(source="pk")
    firstName = serializers.CharField(source="first_name")
    lastName = serializers.CharField(source="last_name")
    displayName = serializers.CharField(source="display_name")
    dateOfBirth = serializers.DateField(source="date_of_birth")
    gender = serializers.CharField()
    email = serializers.CharField()
    display_email = serializers.CharField()
    contactPhone = serializers.CharField(source="contact_phone")
    image = serializers.SerializerMethodField()
    fullName = serializers.SerializerMethodField(method_name="get_full_name")
    isPoliticalSupport = serializers.BooleanField(source="is_political_support")
    isAgir = serializers.BooleanField(source="is_agir")
    groups = serializers.SerializerMethodField()
    address1 = serializers.CharField(source="location_address1")
    address2 = serializers.CharField(source="location_address2")
    city = serializers.CharField(source="location_city")
    zip = serializers.CharField(source="location_zip")
    departement = serializers.SerializerMethodField(read_only=True)
    country = CountryField(source="location_country")
    activeContribution = serializers.SerializerMethodField(
        method_name="get_active_contribution"
    )
    actionRadius = serializers.IntegerField(source="action_radius")
    newsletters = PersonNewsletterListField(read_only=True)
    membreReseauElus = serializers.SerializerMethodField(
        method_name="is_membre_reseau_elus", read_only=True
    )
    votingProxyId = serializers.SerializerMethodField(method_name="get_voting_proxy_id")

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_image(self, obj):
        if obj.image and obj.image.thumbnail:
            return obj.image.thumbnail.url

    def get_departement(self, obj):
        return obj.get_departement()

    def get_groups(self, obj):
        person_groups = (
            SupportGroup.objects.filter(memberships__person=obj)
            .active()
            .annotate(membership_type=F("memberships__membership_type"))
            .order_by("-membership_type", "name")
        )

        return [
            {
                "id": group.id,
                "name": group.name,
                "link": reverse("view_group", kwargs={"pk": group.pk}),
                "isManager": (
                    group.membership_type >= Membership.MEMBERSHIP_TYPE_MANAGER
                ),
                "isReferent": (
                    group.membership_type == Membership.MEMBERSHIP_TYPE_REFERENT
                ),
            }
            for group in person_groups
        ]

    def get_active_contribution(self, obj):
        active_contribution = get_active_contribution_for_person(obj)
        if active_contribution:
            return {
                "id": active_contribution.id,
                "amount": active_contribution.price,
                "endDate": get_contribution_end_date(active_contribution),
                "renewable": is_renewable_contribution(active_contribution),
            }

        return None

    def is_membre_reseau_elus(self, obj):
        return obj.membre_reseau_elus == obj.MEMBRE_RESEAU_OUI

    def get_voting_proxy_id(self, obj):
        accepted_voting_proxy_request = (
            VotingProxyRequest.objects.filter(proxy__person_id=obj.id)
            .upcoming()
            .only("proxy_id")
            .first()
        )
        if accepted_voting_proxy_request:
            return accepted_voting_proxy_request.proxy_id


class SessionSerializer(serializers.Serializer):
    user = serializers.SerializerMethodField(method_name="get_user", read_only=True)
    toasts = serializers.SerializerMethodField(method_name="get_toasts", read_only=True)
    routes = serializers.SerializerMethodField(
        method_name="get_user_routes", read_only=True
    )
    facebookLogin = serializers.SerializerMethodField(
        method_name="get_facebook_login", read_only=True
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
            "resources": "https://infos.actionpopulaire.fr",
            "logout": reverse("disconnect"),
            "personalInformation": reverse("personal_information"),
            "nspReferral": front_url("nsp_referral"),
            "materiel": "https://materiel.actionpopulaire.fr/",
            "news": "https://lafranceinsoumise.fr/actualites/",
            "thematicTeams": front_url("thematic_groups"),
        }

        if request.user.is_authenticated and request.user.person is not None:
            routes.update(
                {
                    "notificationSettings": reverse(
                        "list_activities.notification_settings"
                    )
                }
            )

            return routes

    def get_toasts(self, request):
        return [
            {
                "toastId": uuid.uuid4(),
                "message": m.message,
                "html": True,
                "type": m.level_tag.upper(),
                "tags": m.extra_tags,
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

    def get_bookmarked_emails(self, request):
        return get_bookmarked_emails(request)


class SessionDonationSerializer(serializers.Serializer):
    donations = serializers.SerializerMethodField(read_only=True)

    def get_donations(self, request):
        if DONATION_SESSION_NAMESPACE in request.session:
            return request.session[DONATION_SESSION_NAMESPACE]
        else:
            return None
