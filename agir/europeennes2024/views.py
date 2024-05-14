from django.urls import reverse_lazy
from django.views.generic import RedirectView

from agir.loans.forms import LenderForm
from agir.loans.views import BaseLoanPersonalInformationView, BaseLoanAcceptContractView

from .apps import Europeennes2024Config
from .payment_mode import (
    Europeennes2024PretsPaymentMode,
    Europeennes2024DonsPaymentMode,
)
from ..donations.base_views import BasePersonalInformationView

don_success_view = RedirectView.as_view(
    url="https://lafranceinsoumise.fr/europeennes-2024/don/merci/"
)

pret_success_view = RedirectView.as_view(
    url="https://lafranceinsoumise.fr/europeennes-2024/pret/merci/"
)


class ConfigurationPretsEuropeennes:
    first_step_url = "https://lafranceinsoumise.fr/europeennes-2024/"
    payment_type = Europeennes2024Config.LOAN_TYPE
    payment_modes = [Europeennes2024PretsPaymentMode]


class ConfigurationDonsEuropeennes:
    first_step_url = "https://lafranceinsoumise.fr/europeennes-2024/"
    payment_type = Europeennes2024Config.DONATION_TYPE
    payment_modes = [Europeennes2024DonsPaymentMode]


class PretsPersonalInformationView(
    ConfigurationPretsEuropeennes, BaseLoanPersonalInformationView
):
    template_name = "europeennes2024/informations_prets.html"
    form_class = LenderForm
    success_url = reverse_lazy("europeennes2024:contrat_prets")


class PretsReviewContractView(
    ConfigurationPretsEuropeennes, BaseLoanAcceptContractView
):
    template_name = "loans/sample/validate_contract.html"


class DonsPersonalInformationView(
    ConfigurationDonsEuropeennes, BasePersonalInformationView
):
    template_name = "europeennes2024/informations_dons.html"
