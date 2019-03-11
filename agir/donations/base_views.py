from django.db import transaction
from django.shortcuts import redirect
from django.views.generic import FormView, UpdateView

import agir.donations.base_forms
from agir.donations.apps import DonsConfig
from agir.payments.actions import create_payment, redirect_to_payment
from agir.people.models import Person


class BaseAskAmountView(FormView):
    form_class = agir.donations.base_forms.SimpleDonationForm
    session_namespace = "_donation_"

    def dispatch(self, request, *args, **kwargs):
        self.data_to_persist = request.session[self.session_namespace] = {}
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Enregistre le montant dans la session avant de rediriger vers le formulaire suivant.
        """
        amount = int(form.cleaned_data["amount"] * 100)
        self.data_to_persist["amount"] = amount

        return super().form_valid(form)


class BasePersonalInformationView(UpdateView):
    form_class = agir.donations.base_forms.SimpleDonorForm
    template_name = "donations/personal_information.html"
    payment_mode = None
    session_namespace = "_donation_"

    def dispatch(self, request, *args, **kwargs):
        if not isinstance(request.session.get(self.session_namespace, None), dict):
            return redirect("donation_amount")

        self.persistent_data = request.session[self.session_namespace]
        return super().dispatch(request, *args, **kwargs)

    def clear_session(self):
        del self.request.session[self.session_namespace]

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
        return {**super().get_form_kwargs(), **self.persistent_data}

    def get_context_data(self, **kwargs):
        return super().get_context_data(amount=self.persistent_data["amount"], **kwargs)

    def get_payment_metas(self, form):
        return {"nationality": form.cleaned_data["nationality"]}

    def form_valid(self, form):
        person = form.save()
        amount = self.persistent_data["amount"]
        payment_metas = self.get_payment_metas(form)

        with transaction.atomic():
            payment = create_payment(
                person=person,
                mode=self.payment_mode,
                type=DonsConfig.PAYMENT_TYPE,
                price=amount,
                meta=payment_metas,
            )

        self.clear_session()

        return redirect_to_payment(payment)
