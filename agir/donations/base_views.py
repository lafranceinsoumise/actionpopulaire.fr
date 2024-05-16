from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic import FormView

from agir.donations.base_forms import SimpleDonationForm, SimpleDonorForm
from agir.donations.allocations import get_allocation_list
from agir.payments.actions.payments import create_payment


def serialize_form(form):
    data = form.cleaned_data
    return {k: form[k].data for k in data}


class FormToSessionMixin:
    session_namespace = None

    def form_valid(self, form):
        """Enregistre le contenu du formulaire dans la session avant de rediriger vers le formulaire suivant."""
        self.request.session[self.session_namespace] = serialize_form(form)
        return super().form_valid(form)


class BaseAskAmountView(FormToSessionMixin, FormView):
    form_class = SimpleDonationForm
    session_namespace = "_donation_"


class BasePersonalInformationView(FormView):
    form_class = SimpleDonorForm
    template_name = "donations/personal_information.html"
    payment_type = None
    payment_modes = None
    session_namespace = "_donation_"
    first_step_url = None
    persisted_data = ["amount"]

    def redirect_to_first_step(self):
        return redirect(self.first_step_url)

    def dispatch(self, request, *args, **kwargs):
        self.persistent_data = {}
        form_class = self.form_class
        for k in self.persisted_data:
            field = form_class.declared_fields[k]

            if k in request.GET:
                value = request.GET[k]
            elif k in request.session.get(self.session_namespace, {}):
                value = request.session[self.session_namespace][k]
            else:
                value = field.initial

            try:
                value = field.clean(value)
            except ValidationError:
                return self.redirect_to_first_step()

            self.persistent_data[k] = value

        return super().dispatch(request, *args, **kwargs)

    def clear_session(self):
        if self.session_namespace in self.request.session:
            del self.request.session[self.session_namespace]

    def get_person(self, queryset=None):
        if self.request.user.is_authenticated:
            return self.request.user.person
        else:
            return None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        initial = kwargs.pop("initial", {})
        if self.payment_modes:
            kwargs.update({"payment_modes": self.payment_modes})
        return {
            **kwargs,
            "initial": {**initial, **self.persistent_data},
            "instance": self.get_person(),
        }

    def get_context_data(self, **kwargs):
        if "allocations" in kwargs:
            kwargs["allocations"] = get_allocation_list(
                kwargs["allocations"], with_labels=True
            )

        return super().get_context_data(**self.persistent_data, **kwargs)

    def get_metas(self, form):
        ignore_fields = [
            "payment_mode",
        ]

        return {
            **{
                k: v for k, v in form.cleaned_data.items() if k not in ignore_fields
            },  # person fields
            "contact_phone": form.cleaned_data["contact_phone"].as_e164,
            "utm_source": self.request.GET.get("utm_source", ""),
            "utm_medium": self.request.GET.get("utm_medium", ""),
            "utm_campaign": self.request.GET.get("utm_campaign", ""),
        }

    def form_valid(self, form):
        if form.connected:
            person = form.save()
            email = person.email
        else:
            person = None
            email = form.cleaned_data["email"]

        payment_mode = form.cleaned_data["payment_mode"].id
        amount = form.cleaned_data["amount"]
        meta = self.get_metas(form)

        payment = create_payment(
            person=person,
            email=email,
            type=self.payment_type,
            mode=payment_mode,
            price=amount,
            meta=meta,
        )

        return HttpResponseRedirect(payment.get_payment_url())
