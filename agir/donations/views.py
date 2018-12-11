import reversion
from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils.translation import ugettext as _
from django.views.generic import (
    FormView,
    UpdateView,
    TemplateView,
    DetailView,
    CreateView,
)

from agir.authentication.view_mixins import HardLoginRequiredMixin
from agir.donations.actions import (
    summary,
    history,
    can_send_for_review,
    send_for_review,
    group_can_handle_allocation,
)
from agir.donations.forms import (
    DocumentOnCreationFormset,
    DocumentHelper,
    SpendingRequestCreationForm,
    DocumentForm,
)
from agir.groups.models import SupportGroup, Membership
from agir.payments.actions import create_payment, redirect_to_payment
from agir.payments.models import Payment
from agir.people.models import Person
from . import forms
from .apps import DonsConfig
from .models import SpendingRequest, Operation, Document
from .tasks import send_donation_email

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
        allocation = int(form.cleaned_data.get("allocation", 0) * 100)

        self.request.session[session_key("amount")] = amount
        self.request.session[session_key("allocation")] = allocation
        self.request.session[session_key("group")] = form.group and str(form.group.pk)
        return super().form_valid(form)


class PersonalInformationView(UpdateView):
    form_class = forms.DonorForm
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
        kwargs["allocation"] = self.request.session.get(session_key("allocation"), 0)
        kwargs["group_id"] = self.request.session.get(session_key("group"), None)

        return kwargs

    def get_context_data(self, **kwargs):
        amount = self.request.session[session_key("amount")]
        allocation = self.request.session.get(session_key("allocation"), 0)
        group_id = self.request.session.get(session_key("group"), None)
        group_name = None

        if group_id:
            try:
                group_name = SupportGroup.objects.get(pk=group_id).name
            except SupportGroup.DoesNotExist:
                pass

        return super().get_context_data(
            amount=amount,
            allocation=allocation,
            national=amount - allocation,
            group_name=group_name,
            **kwargs
        )

    def form_valid(self, form):
        person = form.save()
        amount = form.cleaned_data["amount"]
        allocation = form.cleaned_data["allocation"]
        group = form.cleaned_data["group"]

        with transaction.atomic():
            if allocation and group:
                allocation_metas = {"allocation": allocation, "group_id": str(group.id)}
            else:
                allocation_metas = {}
            payment = create_payment(
                person=person,
                type=DonsConfig.PAYMENT_TYPE,
                price=amount,
                meta={"nationality": person.meta["nationality"], **allocation_metas},
            )

        del self.request.session[session_key("amount")]
        if session_key("allocation") in self.request.session:
            del self.request.session[session_key("allocation")]
        if session_key("group") in self.request.session:
            del self.request.session[session_key("group")]

        return redirect_to_payment(payment)


class ReturnView(TemplateView):
    template_name = "donations/thanks.html"


def notification_listener(payment):
    if payment.status == Payment.STATUS_COMPLETED:
        send_donation_email.delay(payment.person.pk)

        if (
            payment.meta.get("allocation") is not None
            and payment.meta.get("group_id") is not None
        ):
            Operation.objects.create(
                payment=payment,
                group_id=payment.meta.get("group_id"),
                amount=payment.meta.get("allocation"),
            )


class CreateSpendingRequestView(HardLoginRequiredMixin, TemplateView):
    template_name = "donations/create_spending_request.html"

    def is_authorized(self, request):
        return (
            super().is_authorized(request)
            and group_can_handle_allocation(self.group)
            and Membership.objects.filter(
                person=request.user.person, supportgroup=self.group, is_manager=True
            ).exists()
        )

    def dispatch(self, request, *args, **kwargs):
        try:
            self.group = SupportGroup.objects.get(pk=self.kwargs["group_id"])
        except SupportGroup.DoesNotExist:
            raise Http404()

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.spending_request = None
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        self.spending_request = None
        spending_request_form, document_formset = self.get_forms()
        if spending_request_form.is_valid() and document_formset.is_valid():
            return self.form_valid(spending_request_form, document_formset)
        return self.form_invalid(spending_request_form, document_formset)

    def form_valid(self, spending_request_form, document_formset):
        with reversion.create_revision():
            reversion.set_user(self.request.user)
            reversion.set_comment("Création de la demande de dépense")

            self.spending_request = spending_request_form.save()
            document_formset.save()

        return HttpResponseRedirect(
            reverse("manage_spending_request", kwargs={"pk": self.spending_request.pk})
        )

    def form_invalid(self, spending_request_form, document_formset):
        return self.render_to_response(
            self.get_context_data(
                spending_request_form=spending_request_form,
                document_formset=document_formset,
            )
        )

    def get_forms(self):
        kwargs = {}
        if self.request.method in ("POST", "PUT"):
            kwargs.update({"data": self.request.POST, "files": self.request.FILES})

        spending_request_form = SpendingRequestCreationForm(
            group=get_object_or_404(
                SupportGroup.objects.active(), id=self.kwargs["group_id"]
            ),
            user=self.request.user,
            **kwargs
        )
        document_formset = DocumentOnCreationFormset(
            instance=spending_request_form.instance, **kwargs
        )

        return spending_request_form, document_formset

    def get_context_data(self, **kwargs):
        if "spending_request_form" not in kwargs or "document_formset" not in kwargs:
            spending_request, document_formset = self.get_forms()
            kwargs["spending_request_form"] = spending_request
            kwargs["document_formset"] = document_formset
        kwargs["document_helper"] = DocumentHelper()
        return super().get_context_data(**kwargs)


class IsGroupManagerMixin(HardLoginRequiredMixin):
    spending_request_pk_field = "pk"

    def is_authorized(self, request):
        return super().is_authorized(request) and Membership.objects.filter(
            person=request.user.person,
            supportgroup__spending_request__id=self.kwargs[
                self.spending_request_pk_field
            ],
            is_manager=True,
        )


class ManageSpendingRequestView(IsGroupManagerMixin, DetailView):
    model = SpendingRequest
    template_name = "donations/manage_spending_request.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            supportgroup=self.object.group,
            documents=self.object.documents.all(),
            can_send_for_review=can_send_for_review(self.object, self.request.user),
            summary=summary(self.object),
            history=history(self.object),
            **kwargs
        )

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        validate = self.request.POST.get("validate")

        if validate != self.object.status or not send_for_review(
            self.object, request.user
        ):
            messages.add_message(
                request,
                messages.WARNING,
                _("Vous ne pouvez pas valider cette demande."),
            )

        return HttpResponseRedirect(
            reverse("manage_spending_request", args=(self.object.pk,))
        )


class EditSpendingRequestView(IsGroupManagerMixin, UpdateView):
    model = SpendingRequest
    form_class = forms.SpendingRequestEditForm
    template_name = "donations/edit_spending_request.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse("manage_spending_request", args=(self.object.pk,))


class CreateDocument(IsGroupManagerMixin, CreateView):
    model = Document
    form_class = DocumentForm
    spending_request_pk_field = "spending_request_id"
    template_name = "donations/create_document.html"

    def get(self, *args, **kwargs):
        self.spending_request = get_object_or_404(
            SpendingRequest, pk=self.kwargs["spending_request_id"]
        )
        return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        self.spending_request = get_object_or_404(
            SpendingRequest, pk=self.kwargs["spending_request_id"]
        )
        return super().post(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["spending_request"] = self.spending_request
        return kwargs

    def get_success_url(self):
        return reverse("manage_spending_request", args=(self.spending_request.pk,))

    def form_valid(self, form):
        with reversion.create_revision():
            reversion.set_user(user=self.request.user)
            reversion.set_comment(_("Création du document"))
            self.object = form.save()

        return HttpResponseRedirect(self.get_success_url())


class EditDocument(IsGroupManagerMixin, UpdateView):
    model = Document
    form_class = DocumentForm
    spending_request_pk_field = "spending_request_id"
    template_name = "donations/edit_document.html"

    def get(self, *args, **kwargs):
        self.spending_request = get_object_or_404(
            SpendingRequest,
            pk=self.kwargs["spending_request_id"],
            document__pk=self.kwargs["pk"],
        )

        return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        self.spending_request = get_object_or_404(
            SpendingRequest,
            pk=self.kwargs["spending_request_id"],
            document__pk=self.kwargs["pk"],
        )
        return super().post(*args, **kwargs)

    def get_success_url(self):
        return reverse("manage_spending_request", args=(self.spending_request.pk,))

    def form_valid(self, form):
        with reversion.create_revision():
            reversion.set_user(user=self.request.user)
            reversion.set_comment(_("Modification du document"))
            self.object = form.save()

        return HttpResponseRedirect(self.get_success_url())
