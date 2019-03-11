from urllib.parse import urljoin

from django.conf import settings
from django.urls import reverse_lazy
from django.views.generic import FormView

from agir.donations.views import BasePersonalInformationView
from agir.donations.base_views import BaseAskAmountView
from agir.europeennes import AFCESystemPayPaymentMode
from agir.front.view_mixins import SimpleOpengraphMixin


DONATIONS_SESSION_NAMESPACE = "_europeennes_donations"


class DonationAskAmountView(SimpleOpengraphMixin, BaseAskAmountView):
    meta_title = "Je donne à la campagne France insoumise pour les élections européennes le 26 mai"
    meta_description = (
        "Nos 79 candidats, menés par Manon Aubry, la tête de liste, sillonent déjà le pays. Ils ont"
        " besoin de votre soutien pour pouvoir mener cette campagne. Votre contribution sera décisive !"
    )
    meta_type = "website"
    meta_image = urljoin(
        urljoin(settings.FRONT_DOMAIN, settings.STATIC_URL), "europeennes/dons.jpg"
    )
    template_name = "europeennes/donations/ask_amount.html"
    success_url = reverse_lazy("europeennes_donation_information")
    session_namespace = DONATIONS_SESSION_NAMESPACE


class DonationPersonalInformationView(BasePersonalInformationView):
    template_name = "europeennes/donations/personal_information.html"
    payment_mode = AFCESystemPayPaymentMode.id
    session_namespace = DONATIONS_SESSION_NAMESPACE
