from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.views.generic import FormView, UpdateView

import agir.donations.base_forms


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
    payment_type = None
    session_namespace = "_donation_"
    base_redirect_url = None
    persisted_data = ["amount"]

    def return_to_previous_step(self):
        return redirect(self.base_redirect_url)

    def dispatch(self, request, *args, **kwargs):
        self.persistent_data = {}
        for k in self.persisted_data:
            field = self.form_class.base_fields[k]

            if k in request.GET:
                value = request.GET[k]
            elif k in request.session.get(self.session_namespace, {}):
                value = request.session[self.session_namespace][k]
            else:
                value = field.initial

            try:
                value = field.clean(value)
            except ValidationError:
                return self.return_to_previous_step()

            self.persistent_data[k] = value

        return super().dispatch(request, *args, **kwargs)

    def clear_session(self):
        del self.request.session[self.session_namespace]

    def get_object(self, queryset=None):
        if self.request.user.is_authenticated:
            return self.request.user.person
        else:
            return None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        initial = kwargs.pop("initial", {})

        return {**kwargs, "initial": {**initial, **self.persistent_data}}

    def get_context_data(self, **kwargs):
        return super().get_context_data(**self.persistent_data, **kwargs)

    def get_metas(self, form):
        return {
            "nationality": form.cleaned_data["nationality"],
            **{
                k: v for k, v in form.cleaned_data.items() if k in form._meta.fields
            },  # person fields
            "contact_phone": form.cleaned_data["contact_phone"].as_e164,
        }
