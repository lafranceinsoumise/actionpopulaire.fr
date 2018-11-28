from django.db import transaction
from django.views.generic import FormView, UpdateView, TemplateView
from django.urls import reverse_lazy
from django.shortcuts import redirect

from agir.donations.models import DonationAllocation
from .apps import DonsConfig
from .tasks import send_donation_email
from ..people.models import Person
from ..payments.actions import create_payment, redirect_to_payment
from ..payments.models import Payment

from . import forms


__all__ = ("AskAmountView", "PersonalInformationView")


SESSION_DONATION_PREFIX = "_donation_"


def session_key(key):
    return SESSION_DONATION_PREFIX + key


class AskAmountView(FormView):
    form_class = forms.DonationForm
    template_name = "donations/ask_amount.html"
    success_url = reverse_lazy("donation_information")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["group_id"] = self.request.GET.get("group")
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        amount = int(form.cleaned_data["amount"] * 100)
        # use int to floor down the value as well as converting to an int
        allocation = int(form.cleaned_data.get("allocation", 0) * amount / 100)

        self.request.session[session_key("amount")] = amount
        self.request.session[session_key("allocation")] = allocation
        self.request.session[session_key("group")] = form.group and str(form.group.pk)
        return super().form_valid(form)


class PersonalInformationView(UpdateView):
    form_class = forms.DonatorForm
    template_name = "donations/personal_information.html"

    def dispatch(self, request, *args, **kwargs):
        if session_key("amount") not in request.session:
            return redirect("donation_amount")
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if self.request.user.is_authenticated:
            return self.request.user.person

        form = self.get_form()
        if form.is_valid():
            try:
                return Person.objects.get_by_natural_key(form.cleaned_data["email"])
            except Person.DoesNotExist:
                pass

        return None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["amount"] = self.request.session[session_key("amount")]
        kwargs["allocation"] = self.request.session[session_key("allocation")]
        kwargs["group_id"] = self.request.session[session_key("group")]
        return kwargs

    def form_valid(self, form):
        person = form.save()
        amount = form.cleaned_data["amount"]
        allocation = form.cleaned_data["allocation"]
        group = form.cleaned_data["group"]

        with transaction.atomic():
            payment = create_payment(
                person=person,
                type=DonsConfig.PAYMENT_TYPE,
                price=amount,
                meta={"nationality": person.meta["nationality"]},
            )
            if allocation and group:
                DonationAllocation.objects.create(
                    payment=payment, group=group, amount=allocation
                )

        return redirect_to_payment(payment)


class ReturnView(TemplateView):
    template_name = "donations/thanks.html"


def notification_listener(payment):
    if payment.status == Payment.STATUS_COMPLETED:
        send_donation_email.delay(payment.person.pk)
