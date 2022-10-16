from django.db.models import F, Prefetch
from django.utils.decorators import method_decorator
from django.views.decorators import cache
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import RetrieveAPIView, get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from agir.donations.views import MonthlyDonationEmailConfirmationView
from agir.groups.models import Membership, SupportGroup
from agir.lib.rest_framework_permissions import IsPersonOrTokenHasScopePermission
from agir.people.models import Person
from agir.presidentielle2022 import AFCP2022SystemPayPaymentMode
from agir.presidentielle2022.actions import get_aggregates
from agir.presidentielle2022.apps import Presidentielle2022Config
from agir.presidentielle2022.serializers import TokTokUserSerializer


class MonthlyDonation2022EmailConfirmationView(MonthlyDonationEmailConfirmationView):
    payment_mode = AFCP2022SystemPayPaymentMode.id
    payment_type = Presidentielle2022Config.DONATION_SUBSCRIPTION_TYPE


class PublicDonation2022AggregatesAPIView(APIView):
    permission_classes = (AllowAny,)

    @method_decorator(cache_page(60))
    @method_decorator(cache.cache_control(public=True))
    def get(self, request, *args, **kwargs):
        return Response(get_aggregates())


@method_decorator(vary_on_headers("Authorization"), name="get")
class TokTokAPIView(RetrieveAPIView):
    permission_classes = (IsPersonOrTokenHasScopePermission,)
    required_scopes = ("toktok",)
    queryset = Person.objects.all()
    serializer_class = TokTokUserSerializer

    def get_object(self):
        person = get_object_or_404(
            Person.objects.prefetch_related(
                Prefetch(
                    "supportgroups",
                    queryset=(
                        SupportGroup.objects.filter(
                            memberships__person_id=self.request.user.person.id
                        )
                        .active()
                        .certified()
                        .annotate(membership_type=F("memberships__membership_type"))
                        .filter(membership_type__gte=Membership.MEMBERSHIP_TYPE_MEMBER)
                        .order_by("-membership_type", "name")
                    ),
                    to_attr="certified_groups_with_active_membership",
                )
            ).all(),
            id=self.request.user.person.id,
        )

        if len(person.certified_groups_with_active_membership) == 0:
            raise PermissionDenied(detail={"error": "not_a_group_member"})

        return person
