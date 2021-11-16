from django.db.models import Sum
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from agir.donations.views import (
    MonthlyDonationPersonalInformationView,
    MonthlyDonationEmailConfirmationView,
)
from agir.lib.rest_framework_permissions import GlobalOnlyPermissions
from agir.payments.models import Payment
from agir.people.models import Person
from agir.presidentielle2022 import AFCP2022SystemPayPaymentMode
from agir.presidentielle2022.apps import Presidentielle2022Config


class MonthlyDonation2022PersonalInformationView(
    MonthlyDonationPersonalInformationView
):
    template_name = "presidentielle2022/donations/personal_information_2022.html"
    payment_type = Presidentielle2022Config.DONATION_SUBSCRIPTION_TYPE
    payment_mode = AFCP2022SystemPayPaymentMode.id
    first_step_url = "donations_2022_amount"
    confirmation_view_name = "monthly_donation_2022_confirm"


class MonthlyDonation2022EmailConfirmationView(MonthlyDonationEmailConfirmationView):
    payment_mode = AFCP2022SystemPayPaymentMode.id
    payment_type = Presidentielle2022Config.DONATION_SUBSCRIPTION_TYPE


class Donation2022AggregatesAPIView(GenericAPIView):
    queryset = Person.objects.all()  # pour les permissions
    permission_classes = (GlobalOnlyPermissions,)

    def get_aggregates(self):
        return (
            Payment.objects.completed()
            .filter(
                type__in=[
                    Presidentielle2022Config.DONATION_PAYMENT_TYPE,
                    Presidentielle2022Config.DONATION_SUBSCRIPTION_TYPE,
                ]
            )
            .aggregate(totalAmount=Sum("price"))
        )

    @method_decorator(vary_on_headers("Authorization"))
    @method_decorator(cache_page(60))
    def get(self, request, *args, **kwargs):
        return Response(self.get_aggregates())
