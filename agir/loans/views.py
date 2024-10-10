from functools import partial
from wsgiref.util import FileWrapper

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.files.storage import default_storage
from django.db import transaction
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import FormView, TemplateView, DetailView

from agir.authentication.view_mixins import SoftLoginRequiredMixin
from agir.donations.base_views import BaseAskAmountView, BasePersonalInformationView
from agir.front.view_mixins import SimpleOpengraphMixin
from agir.loans import tasks
from agir.loans.actions import generate_html_contract
from agir.loans.display import SUBSTITUTIONS
from agir.loans.forms import LoanForm, LenderForm, ContractForm
from agir.loans.loan_config import LoanConfiguration
from agir.payments.actions.payments import (
    create_payment,
    redirect_to_payment,
    find_or_create_person_from_payment,
)
from agir.payments.models import Payment
from agir.payments.types import PAYMENT_TYPES

LOANS_INFORMATION_SESSION_NAMESPACE = "loans"
LOANS_CONTRACT_SESSION_NAMESPACE = "loans_contract"


class MaxTotalLoanMixin:
    def dispatch(self, *args, **kwargs):
        loan_config = PAYMENT_TYPES[self.payment_type]

        if loan_config.global_ceiling and (
            Payment.objects.filter(
                type=self.payment_type, status=Payment.STATUS_COMPLETED
            ).aggregate(amount=Coalesce(Sum("price"), 0))["amount"]
            > loan_config.global_ceiling
        ):
            return HttpResponseRedirect(
                "https://lafranceinsoumise.fr/europeennes-2024/merci"
            )

        return super().dispatch(*args, **kwargs)


class BaseLoanAskAmountView(MaxTotalLoanMixin, SimpleOpengraphMixin, BaseAskAmountView):
    meta_title = None
    meta_description = None
    meta_type = "website"
    meta_image = None
    template_name = "loans/sample/ask_amount.html"
    success_url = None
    form_class = LoanForm
    session_namespace = LOANS_INFORMATION_SESSION_NAMESPACE
    payment_type: LoanConfiguration = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["loan_configuration"] = PAYMENT_TYPES[self.payment_type]
        return kwargs


class BaseLoanPersonalInformationView(MaxTotalLoanMixin, BasePersonalInformationView):
    template_name = "loans/sample/personal_information.html"
    session_namespace = LOANS_INFORMATION_SESSION_NAMESPACE
    form_class = LenderForm
    first_step_url = None
    success_url = None
    payment_type = None
    payment_modes = []

    def get_payment_modes(self):
        return self.payment_modes

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["payment_modes"] = self.get_payment_modes()
        kwargs["loan_configuration"] = PAYMENT_TYPES[self.payment_type]
        return kwargs

    def prepare_data_for_serialization(self, data):
        return {
            **data,
            "contact_phone": data["contact_phone"].as_e164,
            "date_of_birth": data["date_of_birth"].strftime("%d/%m/%Y"),
            "payment_mode": data["payment_mode"].id,
            "iban": data["iban"],
        }

    def form_valid(self, form):
        if form.connected:
            form.save()

        # il faut assigner un nouveau dictionnaire plutôt que d'updater le précédent
        #
        self.request.session[self.session_namespace] = {
            **self.request.session.get(self.session_namespace, {}),
            "__contract": self.prepare_data_for_serialization(form.cleaned_data),
        }

        return HttpResponseRedirect(self.get_success_url())


class BaseLoanAcceptContractView(MaxTotalLoanMixin, FormView):
    form_class = ContractForm
    template_name = "loans/sample/validate_contract.html"
    payment_type = None
    session_namespace = LOANS_INFORMATION_SESSION_NAMESPACE
    first_step_url = None

    def redirect_to_first_step(self):
        return redirect(self.first_step_url)

    def dispatch(self, request, *args, **kwargs):
        if (
            self.session_namespace not in request.session
            or "__contract" not in request.session[self.session_namespace]
        ):
            return self.redirect_to_first_step()

        self.contract_information = request.session[self.session_namespace][
            "__contract"
        ]

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            contract=generate_html_contract(
                PAYMENT_TYPES[self.payment_type],
                self.contract_information,
            ),
            **self.contract_information,
            **kwargs
        )

    def clear_session(self):
        del self.request.session[self.session_namespace]

    def form_valid(self, form):
        self.contract_information["signature_datetime"] = (
            timezone.now().astimezone(timezone.get_default_timezone()).isoformat()
        )

        person = None
        if self.request.user.is_authenticated:
            person = self.request.user.person

        payment_fields = [f.name for f in Payment._meta.get_fields()]

        kwargs = {
            f: v for f, v in self.contract_information.items() if f in payment_fields
        }
        if "email" in self.contract_information:
            kwargs["email"] = self.contract_information["email"]

        with transaction.atomic():
            self.payment = create_payment(
                person=person,
                mode=self.contract_information["payment_mode"],
                type=self.payment_type,
                price=self.contract_information["amount"],
                meta=self.contract_information,
                **kwargs
            )

        self.clear_session()

        return redirect_to_payment(self.payment)


class LoanReturnView(TemplateView):
    def get_context_data(self, **kwargs):
        gender = self.kwargs["payment"].meta["gender"]

        return super().get_context_data(
            chere_preteur=SUBSTITUTIONS["cher_preteur"][gender], **kwargs
        )


class LoanContractView(SoftLoginRequiredMixin, DetailView):
    payment_type = None

    queryset = Payment.objects.filter(status=Payment.STATUS_COMPLETED)

    def get(self, request, *args, **kwargs):
        payment = self.get_object()

        if payment.person != request.user.person:
            raise PermissionDenied("Vous n'avez pas le droit d'accéder à cette page.")

        if "contract_path" not in payment.meta:
            raise Http404()

        with default_storage.open(payment.meta["contract_path"], "rb") as f:
            return HttpResponse(FileWrapper(f), content_type="application/pdf")


def generate_and_send_contract(payment_id):
    return (
        tasks.generate_contract.si(payment_id)
        | tasks.send_contract_confirmation_email.si(payment_id)
    ).delay()


def loan_notification_listener(payment):
    if payment.status == Payment.STATUS_COMPLETED:
        find_or_create_person_from_payment(payment)
        generate_and_send_contract(payment.id)
