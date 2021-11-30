from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from agir.donations.views import MonthlyDonationEmailConfirmationView
from agir.lib.rest_framework_permissions import GlobalOnlyPermissions
from agir.people.models import Person
from agir.presidentielle2022 import AFCP2022SystemPayPaymentMode
from agir.presidentielle2022.actions import get_aggregates
from agir.presidentielle2022.apps import Presidentielle2022Config


class MonthlyDonation2022EmailConfirmationView(MonthlyDonationEmailConfirmationView):
    payment_mode = AFCP2022SystemPayPaymentMode.id
    payment_type = Presidentielle2022Config.DONATION_SUBSCRIPTION_TYPE


class PublicDonation2022AggregatesAPIView(GenericAPIView):
    queryset = Person.objects.all()  # pour les permissions
    permission_classes = (GlobalOnlyPermissions,)

    @method_decorator(vary_on_headers("Authorization"))
    @method_decorator(cache_page(60))
    def get(self, request, *args, **kwargs):
        return Response(get_aggregates())


class Donation2022AggregatesAPIView(PublicDonation2022AggregatesAPIView):
    permission_classes = (IsAuthenticated,)
