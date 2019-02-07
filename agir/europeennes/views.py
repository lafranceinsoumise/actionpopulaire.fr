from django.urls import reverse_lazy

from agir.donations.views import (
    AskAmountView as BaseAskAmountView,
    PersonalInformationView as BasePersonalInformationView,
)
from agir.europeennes import AFCESystemPayPaymentMode
from agir.front.view_mixins import SimpleOpengraphMixin


class AskAmountView(SimpleOpengraphMixin, BaseAskAmountView):
    meta_title = "Je donne à la campagne France insoumise pour les élections européennes le 26 mai"
    meta_description = (
        "Nos 79 candidats, menés par Manon Aubry, la tête de liste, sillonent déjà le pays. Ils ont"
        " besoin de votre soutien pour pouvoir mener cette campagne. Votre contribution sera décisive !"
    )
    meta_type = "website"

    enable_allocations = False
    template_name = "europeennes/ask_amount.html"
    success_url = reverse_lazy("europeennes_donation_information")


class PersonalInformationView(BasePersonalInformationView):
    enable_allocations = False
    template_name = "europeennes/personal_information.html"
    payment_mode = AFCESystemPayPaymentMode.id
