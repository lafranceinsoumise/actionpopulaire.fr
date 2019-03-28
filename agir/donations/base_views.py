from django.db import transaction
from django.shortcuts import redirect
from django.views.generic import FormView, UpdateView

import agir.donations.base_forms
from agir.donations.apps import DonsConfig
from agir.payments.actions import create_payment, redirect_to_payment
from agir.payments.models import Payment
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
    base_redirect_url = None

    def dispatch(self, request, *args, **kwargs):
        if (
            not isinstance(request.session.get(self.session_namespace, None), dict)
            or "amount" not in request.session[self.session_namespace]
        ):
            return redirect(self.base_redirect_url)

        self.persistent_data = request.session[self.session_namespace]
        return super().dispatch(request, *args, **kwargs)

    def clear_session(self):
        del self.request.session[self.session_namespace]

    def get_object(self, queryset=None):
        if self.request.user.is_authenticated:
            return self.request.user.person
        else:
            return None

    def get_form_kwargs(self):
        return {**super().get_form_kwargs(), **self.persistent_data}

    def get_context_data(self, **kwargs):
        return super().get_context_data(amount=self.persistent_data["amount"], **kwargs)

    def get_payment_meta(self, form):
        return {
            "nationality": form.cleaned_data["nationality"],
            **{
                k: v for k, v in form.cleaned_data.items() if k in form._meta.fields
            },  # person fields
            "contact_phone": form.cleaned_data["contact_phone"].as_e164,
        }

    def form_valid(self, form):
        if not form.adding:
            self.object = form.save()

        amount = self.persistent_data["amount"]
        payment_metas = self.get_payment_meta(form)

        payment_fields = [f.name for f in Payment._meta.get_fields()]

        kwargs = {f: v for f, v in form.cleaned_data.items() if f in payment_fields}
        if "email" in form.cleaned_data:
            kwargs["email"] = form.cleaned_data["email"]

        with transaction.atomic():
            payment = create_payment(
                person=self.object,
                mode=self.payment_mode,
                type=DonsConfig.PAYMENT_TYPE,
                price=amount,
                meta=payment_metas,
                **kwargs
            )

        self.clear_session()

        return redirect_to_payment(payment)
