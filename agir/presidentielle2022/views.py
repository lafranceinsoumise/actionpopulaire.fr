from django.db.models import Sum
from rest_framework import permissions
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from agir.donations.views import (
    DonationPersonalInformationView,
    MonthlyDonationPersonalInformationView,
    MonthlyDonationEmailConfirmationView,
)
from agir.payments.models import Payment
from agir.presidentielle2022 import (
    AFCP2022SystemPayPaymentMode,
    AFCPJLMCheckDonationPaymentMode,
)
from agir.presidentielle2022.apps import Presidentielle2022Config


class Donation2022PersonalInformationView(DonationPersonalInformationView):
    template_name = "presidentielle2022/donations/personal_information_2022.html"
    payment_type = Presidentielle2022Config.DONATION_PAYMENT_TYPE
    payment_modes = [AFCP2022SystemPayPaymentMode, AFCPJLMCheckDonationPaymentMode]
    first_step_url = "donations_2022_amount"


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


class Donation2022AggregatesAPIView(ListAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = Payment.objects.completed().filter(
        type__in=[
            Presidentielle2022Config.DONATION_PAYMENT_TYPE,
            Presidentielle2022Config.DONATION_SUBSCRIPTION_TYPE,
        ]
    )

    def list(self, request, *args, **kwargs):
        return Response(self.queryset.aggregate(totalAmount=Sum("price")))
