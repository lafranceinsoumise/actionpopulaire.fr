import reversion
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils.functional import cached_property
from django.utils.translation import ugettext as _
from django.views import View
from django.views.generic import UpdateView, TemplateView, DetailView, CreateView
from django.views.generic.detail import SingleObjectMixin

from agir.authentication.tokens import monthly_donation_confirmation_token_generator
from agir.authentication.utils import soft_login
from agir.authentication.view_mixins import (
    HardLoginRequiredMixin,
    VerifyLinkSignatureMixin,
)
from agir.donations.allocations import (
    group_can_handle_allocation,
    create_monthly_allocation,
)
from agir.donations.apps import DonsConfig
from agir.donations.base_views import BaseAskAmountView, BasePersonalInformationView
from agir.donations.forms import (
    DocumentOnCreationFormset,
    DocumentHelper,
    SpendingRequestCreationForm,
    DocumentForm,
)
from agir.donations.spending_requests import (
    summary,
    history,
    EDITABLE_STATUSES,
    can_edit,
    get_current_action,
    validate_action,
)
from agir.groups.models import SupportGroup, Membership
from agir.payments import payment_modes
from agir.payments.actions.payments import (
    find_or_create_person_from_payment,
    redirect_to_payment,
    create_payment,
)
from agir.payments.actions.subscriptions import redirect_to_subscribe
from agir.payments.models import Payment, Subscription
from agir.people.models import Person
from . import forms
from .models import SpendingRequest, Operation, Document
from .tasks import send_donation_email, send_monthly_donation_confirmation_email

__all__ = ("AskAmountView", "DonationPersonalInformationView")

DONATION_SESSION_NAMESPACE = "_donation_"


class AskAmountView(BaseAskAmountView):
    meta_title = "Je donne à la France insoumise"
    meta_description = (
        "Pour financer les dépenses liées à l’organisation d’événements, à l’achat de matériel, au"
        "fonctionnement du site, etc., nous avons besoin du soutien financier de chacun.e d’entre vous !"
    )
    meta_type = "website"

    form_class = forms.AllocationDonationForm
    template_name = "donations/ask_amount.html"
    success_url = reverse_lazy("donation_information")
    session_namespace = DONATION_SESSION_NAMESPACE

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["group_id"] = self.request.GET.get("group")
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        # use int to floor down the value as well as converting to an int
        allocation = int(form.cleaned_data.get("allocation", 0) * 100)
        self.data_to_persist["allocation"] = allocation
        self.data_to_persist["group_id"] = form.group and str(form.group.pk)

        if (
            "type" in form.cleaned_data
            and form.cleaned_data["type"] == form.TYPE_MONTHLY
        ):
            self.success_url = reverse("monthly_donation_information")

        return super().form_valid(form)


class AllocationPersonalInformationMixin:
    def get_context_data(self, **kwargs):
        amount = self.persistent_data["amount"]
        allocation = self.persistent_data.get("allocation", 0)

        kwargs["allocation"] = allocation
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


class DonationPersonalInformationView(
    AllocationPersonalInformationMixin, BasePersonalInformationView
):
    form_class = forms.AllocationDonorForm
    template_name = "donations/personal_information.html"
    payment_mode = payment_modes.DEFAULT_MODE
    payment_type = DonsConfig.PAYMENT_TYPE
    session_namespace = DONATION_SESSION_NAMESPACE
    base_redirect_url = "donation_amount"

    def get_metas(self, form):
        meta = super().get_metas(form)

        allocation = form.cleaned_data["allocation"]
        group = form.cleaned_data["group"]

        if allocation and group:
            meta["allocation"] = allocation
            meta["group_id"] = str(group.pk)

        return meta

    def form_valid(self, form):
        if form.connected:
            self.object = form.save()
        amount = form.cleaned_data["amount"]
        payment_metas = self.get_metas(form)

        payment_fields = [f.name for f in Payment._meta.get_fields()]

        kwargs = {f: v for f, v in form.cleaned_data.items() if f in payment_fields}
        if "email" in form.cleaned_data:
            kwargs["email"] = form.cleaned_data["email"]

        with transaction.atomic():
            payment = create_payment(
                person=self.object,
                mode=self.payment_mode,
                type=self.payment_type,
                price=amount,
                meta=payment_metas,
                **kwargs,
            )

        self.clear_session()

        return redirect_to_payment(payment)


class MonthlyDonationPersonalInformationView(
    AllocationPersonalInformationMixin, BasePersonalInformationView
):
    form_class = forms.AllocationMonthlyDonorForm
    template_name = "donations/personal_information.html"
    payment_mode = payment_modes.DEFAULT_MODE
    payment_type = DonsConfig.PAYMENT_TYPE
    session_namespace = DONATION_SESSION_NAMESPACE
    base_redirect_url = "view_payments"

    def get_context_data(self, **kwargs):
        return super().get_context_data(monthly=True, **kwargs)

    def form_valid(self, form):
        amount = form.cleaned_data["amount"]
        allocation = form.cleaned_data.get("allocation", 0)
        allocation_group = form.cleaned_data.get("group", None)

        if form.connected:
            self.object = form.save()

            if Subscription.objects.filter(
                person=self.object, status=Subscription.STATUS_COMPLETED
            ):
                return HttpResponseRedirect(reverse("already_has_subscription"))

            with transaction.atomic():
                subscription, allocation = create_monthly_allocation(
                    person=self.object,
                    mode=self.payment_mode,
                    subscription_total=amount,
                    allocation_amount=allocation,
                    group=allocation_group,
                    meta=self.get_metas(form),
                )

            self.clear_session()

            return redirect_to_subscribe(subscription)
        else:
            send_monthly_donation_confirmation_email.delay(
                email=form.cleaned_data["email"],
                mode=self.payment_mode,
                subscription_total=amount,
                allocation_amount=allocation,
                group_pk=allocation_group and allocation_group.pk,
                **self.get_metas(form),
            )
            return HttpResponseRedirect(
                reverse("monthly_donation_confirmation_email_sent")
            )


class MonthlyDonationEmailSentView(TemplateView):
    template_name = "donations/monthly_donation_confirmation_email_sent.html"


class AlreadyHasSubscriptionView(TemplateView):
    template_name = "donations/already_has_subscription.html"


class MonthlyDonationEmailConfirmationView(VerifyLinkSignatureMixin, View):
    def get(self, request, *args, **kwargs):
        params = request.GET.dict()

        if "token" not in params:
            return self.link_error_page()

        token = params.pop("token")
        if not monthly_donation_confirmation_token_generator.check_token(
            token, **params
        ):
            return self.link_error_page()

        try:
            email = params.pop("email")
            mode = params.pop("mode")
            subscription_total = int(params.pop("subscription_total"))
            group_pk = params.pop("group_pk", None)
            allocation_amount = int(params.pop("allocation_amount"))
        except KeyError:
            return self.link_error_page()

        if group_pk:
            try:
                group = SupportGroup.objects.get(pk=group_pk)
            except SupportGroup.DoesNotExist:
                group = None
                allocation_amount = 0
        else:
            group = None

        try:
            person = Person.objects.get_by_natural_key(email)
        except Person.DoesNotExist:
            person = Person.objects.create(
                email=email,
                **{
                    f.name: params[f.name]
                    for f in Person._meta.get_fields()
                    if f.name in params
                },
            )

        soft_login(request, person)

        if Subscription.objects.filter(
            person=person, status=Subscription.STATUS_COMPLETED
        ).exists():
            return HttpResponseRedirect(reverse("already_has_subscription"))

        subscription, allocation = create_monthly_allocation(
            person=person,
            mode=mode,
            subscription_total=subscription_total,
            allocation_amount=allocation_amount,
            group=group,
            meta=params,
        )

        return redirect_to_subscribe(subscription)


class ReturnView(TemplateView):
    template_name = "donations/thanks.html"


def subscription_notification_listener(subscription):
    if subscription.status == Subscription.STATUS_COMPLETED:
        send_donation_email.delay(subscription.person.pk)


def notification_listener(payment):
    if payment.status == Payment.STATUS_COMPLETED:
        find_or_create_person_from_payment(payment)
        if payment.subscription is None:
            send_donation_email.delay(payment.person.pk)

        if (
            payment.meta.get("allocation") is not None
            and payment.meta.get("group_id") is not None
        ):
            Operation.objects.update_or_create(
                payment=payment,
                group_id=payment.meta.get("group_id"),
                defaults={"amount": payment.meta.get("allocation")},
            )

        with transaction.atomic():
            if payment.subscription is not None:
                for allocation in payment.subscription.allocations.all():
                    Operation.objects.update_or_create(
                        payment=payment,
                        group=allocation.group,
                        defaults={"amount": allocation.amount},
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
            **kwargs,
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
        return super().is_authorized(request) and self.get_membership(request)

    def get_membership(self, request):
        return Membership.objects.filter(
            person=request.user.person,
            supportgroup__spending_request__id=self.kwargs[
                self.spending_request_pk_field
            ],
        )


class CanEdit(IsGroupManagerMixin):
    def get_membership(self, request):
        return (
            super()
            .get_membership(request)
            .filter(supportgroup__spending_request__status__in=EDITABLE_STATUSES)
        )


class ManageSpendingRequestView(IsGroupManagerMixin, DetailView):
    model = SpendingRequest
    template_name = "donations/manage_spending_request.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            supportgroup=self.object.group,
            documents=self.object.documents.filter(deleted=False),
            can_edit=can_edit(self.object),
            action=get_current_action(self.object, self.request.user),
            summary=summary(self.object),
            history=history(self.object),
            **kwargs,
        )

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        validate = self.request.POST.get("validate")

        if validate != self.object.status or not validate_action(
            self.object, request.user
        ):
            messages.add_message(
                request,
                messages.WARNING,
                _("Il y a eu un problème, veuillez réessayer."),
            )
            return self.render_to_response(self.get_context_data())

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

    def render_to_response(self, context, **response_kwargs):
        if self.object.status in SpendingRequest.STATUS_EDITION_MESSAGES:
            messages.add_message(
                self.request,
                messages.WARNING,
                SpendingRequest.STATUS_EDITION_MESSAGES[self.object.status],
            )
        return super().render_to_response(context, **response_kwargs)


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
        kwargs["user"] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse("manage_spending_request", args=(self.spending_request.pk,))

    def render_to_response(self, context, **response_kwargs):
        if self.spending_request.status in SpendingRequest.STATUS_EDITION_MESSAGES:
            messages.add_message(
                self.request,
                messages.WARNING,
                SpendingRequest.STATUS_EDITION_MESSAGES[self.spending_request.status],
            )
        return super().render_to_response(context, **response_kwargs)


class EditDocument(IsGroupManagerMixin, UpdateView):
    model = Document
    queryset = Document.objects.filter(deleted=False)
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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse("manage_spending_request", args=(self.spending_request.pk,))

    def render_to_response(self, context, **response_kwargs):
        if self.spending_request.status in SpendingRequest.STATUS_EDITION_MESSAGES:
            messages.add_message(
                self.request,
                messages.WARNING,
                SpendingRequest.STATUS_EDITION_MESSAGES[self.object.request.status],
            )

        return super().render_to_response(context, **response_kwargs)


class DeleteDocument(IsGroupManagerMixin, SingleObjectMixin, View):
    model = Document
    spending_request_pk_field = "spending_request_id"

    def post(self, request, *args, **kwargs):
        self.spending_request = get_object_or_404(
            SpendingRequest,
            pk=self.kwargs[self.spending_request_pk_field],
            document__pk=self.kwargs["pk"],
        )
        self.object = self.get_object()

        with reversion.create_revision():
            reversion.set_user(request.user)
            self.object.deleted = True
            self.object.save()

        messages.add_message(
            request, messages.SUCCESS, _("Ce document a bien été supprimé.")
        )

        return HttpResponseRedirect(
            reverse("manage_spending_request", args=(self.spending_request.pk,))
        )
