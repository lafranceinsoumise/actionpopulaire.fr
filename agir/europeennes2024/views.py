from django.urls import reverse_lazy
from django.views.generic import RedirectView, TemplateView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from agir.donations.base_views import BasePersonalInformationView
from agir.loans.forms import LenderForm
from agir.loans.tasks import generate_contract
from agir.loans.views import BaseLoanPersonalInformationView, BaseLoanAcceptContractView
from agir.payments.actions.payments import find_or_create_person_from_payment
from agir.payments.models import Payment
from .apps import Europeennes2024Config
from .compteurs import montant_compteur, incrementer_compteur
from .payment_mode import (
    Europeennes2024PretsPaymentMode,
    Europeennes2024DonsPaymentMode,
    Europeennes2024CheckPaymentMode,
)
from .tasks import envoyer_email_pret, envoyer_email_don

don_success_view = RedirectView.as_view(
    url="https://lafranceinsoumise.fr/europeennes-2024/merci-don/"
)

pret_success_view = RedirectView.as_view(
    url="https://lafranceinsoumise.fr/europeennes-2024/merci-pret/"
)


class ConfigurationPretsEuropeennes:
    first_step_url = "https://lafranceinsoumise.fr/europeennes-2024/emprunt-populaire/"
    payment_type = Europeennes2024Config.LOAN_TYPE
    payment_modes = [Europeennes2024PretsPaymentMode, Europeennes2024CheckPaymentMode]


class ConfigurationDonsEuropeennes:
    first_step_url = "https://lafranceinsoumise.fr/europeennes-2024/emprunt-populaire/"
    payment_type = Europeennes2024Config.DONATION_TYPE
    payment_modes = [Europeennes2024DonsPaymentMode, Europeennes2024CheckPaymentMode]


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

    def form_valid(self, form):
        res = super().form_valid(form)

        if self.payment.mode == Europeennes2024CheckPaymentMode.id:
            incrementer_compteur("prets", self.payment.price)

        return res


class DonsPersonalInformationView(
    ConfigurationDonsEuropeennes, BasePersonalInformationView
):
    template_name = "europeennes2024/informations_dons.html"

    def form_valid(self, form):
        res = super().form_valid(form)

        if self.payment.mode == Europeennes2024CheckPaymentMode.id:
            incrementer_compteur("dons", self.payment.price)

        return res


def pret_status_listener(payment):
    if payment.status == Payment.STATUS_COMPLETED:
        find_or_create_person_from_payment(payment)
        if payment.mode != Europeennes2024CheckPaymentMode.id:
            incrementer_compteur("prets", payment.price)

        return (
            generate_contract.si(payment.id) | envoyer_email_pret.si(payment.id)
        ).delay()


def don_status_listener(payment):
    if payment.status == Payment.STATUS_COMPLETED:
        find_or_create_person_from_payment(payment)
        if payment.mode != Europeennes2024CheckPaymentMode.id:
            incrementer_compteur("dons", payment.price)

        return envoyer_email_don.delay(payment.id)


class MontantView(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)

    def get(self, request):
        return Response(
            {"dons": montant_compteur("dons"), "prets": montant_compteur("prets")}
        )


class CompteurView(TemplateView):
    template_name = "europeennes2024/compteur.html"

    def get_context_data(self, **kwargs):
        if self.request.GET.get("background"):
            kwargs["background"] = self.request.GET["background"]

        return kwargs
