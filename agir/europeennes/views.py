from django.urls import reverse_lazy

from agir.donations.views import (
    AskAmountView as BaseAskAmountView,
    PersonalInformationView as BasePersonalInformationView,
)
from agir.europeennes import AFCESystemPayPaymentMode


class AskAmountView(BaseAskAmountView):
    enable_allocations = False
    template_name = "europeennes/ask_amount.html"
    success_url = reverse_lazy("europeennes_donation_information")


class PersonalInformationView(BasePersonalInformationView):
    enable_allocations = False
    template_name = "europeennes/personal_information.html"
    payment_mode = AFCESystemPayPaymentMode.id
