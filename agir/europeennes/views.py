from urllib.parse import urljoin

from django.conf import settings
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView, TemplateView

from agir.authentication.utils import hard_login
from agir.authentication.view_mixins import SoftLoginRequiredMixin
from agir.checks.views import CheckView
from agir.donations.base_views import BaseAskAmountView
from agir.donations.views import BasePersonalInformationView
from agir.europeennes import AFCESystemPayPaymentMode
from agir.europeennes.actions import generate_html_contract
from agir.europeennes.apps import EuropeennesConfig
from agir.europeennes.forms import LoanForm, ContractForm, LenderForm
from agir.europeennes.tasks import generate_contract, send_contract_confirmation_email
from agir.front.view_mixins import SimpleOpengraphMixin
from agir.payments.actions import create_payment, redirect_to_payment
from agir.payments.models import Payment

DONATIONS_SESSION_NAMESPACE = "_europeennes_donations"
LOANS_INFORMATION_SESSION_NAMESPACE = "_europeennes_loans"
LOANS_CONTRACT_SESSION_NAMESPACE = "_europeennes_loans_contract"


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


class LoanAskAmountView(SimpleOpengraphMixin, BaseAskAmountView):
    meta_title = "Je prête à la campagne France insoumise pour les élections européennes le 26 mai"
    meta_description = (
        "Nos 79 candidats, menés par Manon Aubry, la tête de liste, sillonent déjà le pays. Ils ont"
        " besoin de votre soutien pour pouvoir mener cette campagne. Votre contribution sera décisive !"
    )
    meta_type = "website"
    meta_image = urljoin(
        urljoin(settings.FRONT_DOMAIN, settings.STATIC_URL), "europeennes/dons.jpg"
    )
    template_name = "europeennes/loans/ask_amount.html"
    success_url = reverse_lazy("europeennes_loan_information")
    form_class = LoanForm
    session_namespace = LOANS_INFORMATION_SESSION_NAMESPACE


class LoanPersonalInformationView(BasePersonalInformationView):
    template_name = "europeennes/loans/personal_information.html"
    session_namespace = LOANS_INFORMATION_SESSION_NAMESPACE
    form_class = LenderForm

    def prepare_data_for_serialization(self, data):
        return {
            **data,
            "contact_phone": data["contact_phone"].as_e164,
            "date_of_birth": data["date_of_birth"].strftime("%d/%m/%Y"),
            "payment_mode": data["payment_mode"].id,
            "iban": data["iban"].as_stored_value,
        }

    def form_valid(self, form):
        person = form.save()
        if self.request.user.is_anonymous:
            hard_login(self.request, person)
        self.request.session[
            LOANS_CONTRACT_SESSION_NAMESPACE
        ] = self.prepare_data_for_serialization(form.cleaned_data)

        return HttpResponseRedirect(reverse("europeennes_loan_sign_contract"))


class LoanContractView(SoftLoginRequiredMixin, FormView):
    form_class = ContractForm
    template_name = "europeennes/loans/validate_contract.html"

    def dispatch(self, request, *args, **kwargs):
        if LOANS_CONTRACT_SESSION_NAMESPACE not in request.session:
            if LOANS_INFORMATION_SESSION_NAMESPACE in request.session:
                return HttpResponseRedirect(reverse("europeennes_loan_information"))
            else:
                return HttpResponseRedirect(reverse("europeennes_loan_amount"))

        self.contract_information = request.session[LOANS_CONTRACT_SESSION_NAMESPACE]

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            contract=generate_html_contract(self.contract_information, baselevel=3),
            **self.contract_information,
            **kwargs
        )

    def clear_session(self):
        del self.request.session[LOANS_INFORMATION_SESSION_NAMESPACE]
        del self.request.session[LOANS_CONTRACT_SESSION_NAMESPACE]

    def form_valid(self, form):
        with transaction.atomic():
            payment = create_payment(
                person=self.request.user.person,
                mode=self.contract_information["payment_mode"],
                type=EuropeennesConfig.LOAN_PAYMENT_TYPE,
                price=self.contract_information["amount"],
                meta=self.contract_information,
            )

        self.clear_session()

        return redirect_to_payment(payment)


class LoanReturnView(TemplateView):
    template_name = "europeennes/loans/return.html"


def loan_notification_listener(payment):
    if payment.status == Payment.STATUS_COMPLETED:
        (
            generate_contract.si(payment.id)
            | send_contract_confirmation_email.si(payment.id)
        ).delay()


class AFCECheckView(CheckView):
    template_name = "europeennes/checks/payment.html"
