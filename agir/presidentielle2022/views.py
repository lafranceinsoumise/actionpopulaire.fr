from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from agir.donations.views import MonthlyDonationEmailConfirmationView
from agir.presidentielle2022 import AFCP2022SystemPayPaymentMode
from agir.presidentielle2022.actions import get_aggregates
from agir.presidentielle2022.apps import Presidentielle2022Config


class MonthlyDonation2022EmailConfirmationView(MonthlyDonationEmailConfirmationView):
    payment_mode = AFCP2022SystemPayPaymentMode.id
    payment_type = Presidentielle2022Config.DONATION_SUBSCRIPTION_TYPE


class PublicDonation2022AggregatesAPIView(APIView):
    permission_classes = (AllowAny,)

    @method_decorator(cache_page(60))
    def get(self, request, *args, **kwargs):
        return Response(get_aggregates())
