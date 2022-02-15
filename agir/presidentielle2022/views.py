from django.utils.decorators import method_decorator
from django.views.decorators import cache
from django.views.decorators.cache import cache_page
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from agir.donations.views import MonthlyDonationEmailConfirmationView
from agir.lib.rest_framework_permissions import IsPersonOrTokenHasScopePermission
from agir.presidentielle2022 import AFCP2022SystemPayPaymentMode
from agir.presidentielle2022.actions import get_aggregates
from agir.presidentielle2022.apps import Presidentielle2022Config


class MonthlyDonation2022EmailConfirmationView(MonthlyDonationEmailConfirmationView):
    payment_mode = AFCP2022SystemPayPaymentMode.id
    payment_type = Presidentielle2022Config.DONATION_SUBSCRIPTION_TYPE


class PublicDonation2022AggregatesAPIView(APIView):
    permission_classes = (AllowAny,)

    @method_decorator(cache_page(60))
    @cache.cache_control(public=True)
    def get(self, request, *args, **kwargs):
        return Response(get_aggregates())


class TokTokAPIView(APIView):
    permission_classes = (IsPersonOrTokenHasScopePermission,)
    required_scopes = ("toktok",)

    def get(self, request, *args, **kwargs):
        return Response({"id": request.user.person.id})
