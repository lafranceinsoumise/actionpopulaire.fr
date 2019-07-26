from django.db import transaction
from django.shortcuts import redirect
from django.utils.functional import cached_property
from django.views.generic import FormView, UpdateView

import agir.donations.base_forms
from agir.groups.models import SupportGroup
from agir.payments.actions.payments import create_payment, redirect_to_payment
from agir.payments.models import Payment


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

    def dispatch(self, request, *args, **kwargs):
        self.persistent_data = request.session[self.session_namespace]

        if "amount" in request.GET:
            try:
                amount = int(request.GET["amount"])
            except ValueError:
                pass
            else:
                amount_field = self.form_class.base_fields["amount"]
                if amount_field.min_value <= amount <= amount_field.max_value:
                    request.session[self.session_namespace] = {"amount": amount}

        if (
            not isinstance(request.session.get(self.session_namespace, None), dict)
            or "amount" not in request.session[self.session_namespace]
        ):
            return redirect(self.base_redirect_url)
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

    def get_metas(self, form):
        return {
            "nationality": form.cleaned_data["nationality"],
            **{
                k: v for k, v in form.cleaned_data.items() if k in form._meta.fields
            },  # person fields
            "contact_phone": form.cleaned_data["contact_phone"].as_e164,
        }


class AllocationPersonalInformationMixin:
    enable_allocations = True

    def get_context_data(self, **kwargs):
        amount = self.persistent_data["amount"]
        allocation = self.persistent_data.get("allocation", 0)

        kwargs["allocation"] = 0
        kwargs["national"] = amount - allocation
        kwargs["group_name"] = (
            self.allocation_group.name if self.allocation_group is not None else None
        )

        return super().get_context_data(**kwargs)

    @cached_property
    def allocation_group(self):
        group_id = self.persistent_data.get("group_id", None)

        if group_id is not None:
            return SupportGroup.objects.get(pk=group_id)
