import reversion
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.generic import (
    TemplateView,
    DetailView,
    UpdateView,
    CreateView,
    DeleteView,
)
from django.views.generic.detail import SingleObjectMixin

from agir.authentication.view_mixins import (
    HardLoginRequiredMixin,
    GlobalOrObjectPermissionRequiredMixin,
)
from agir.donations import forms
from agir.donations.forms import (
    SpendingRequestCreationForm,
    DocumentOnCreationFormset,
    DocumentHelper,
    DocumentForm,
)
from agir.donations.models import SpendingRequest, Document
from agir.donations.spending_requests import (
    get_current_action,
    summary,
    validate_action,
)
from agir.groups.models import SupportGroup

__all__ = (
    "CreateSpendingRequestView",
    "EditSpendingRequestView",
    "ManageSpendingRequestView",
    "DeleteSpendingRequestView",
    "CreateDocumentView",
    "EditDocumentView",
    "DeleteDocumentView",
)


@method_decorator(never_cache, name="get")
class CreateSpendingRequestView(
    HardLoginRequiredMixin, GlobalOrObjectPermissionRequiredMixin, TemplateView
):
    template_name = "donations/create_spending_request.html"
    permission_required = ("donations.add_spendingrequest",)

    def get_permission_object(self):
        return self.group

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
            reversion.set_comment("Création de la demande")

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
        kwargs["supportgroup"] = self.group
        kwargs["active"] = "financement"
        return super().get_context_data(**kwargs)


@method_decorator(never_cache, name="get")
class ManageSpendingRequestView(
    HardLoginRequiredMixin, GlobalOrObjectPermissionRequiredMixin, DetailView
):
    model = SpendingRequest
    template_name = "donations/manage_spending_request.html"
    permission_required = ("donations.view_spendingrequest",)

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            spending_request=self.object,
            supportgroup=self.object.group,
            documents=self.object.documents.filter(deleted=False),
            can_edit=self.object.editable,
            can_delete=self.object.deletable,
            action=get_current_action(self.object, self.request.user),
            summary=summary(self.object),
            history=self.object.get_history(),
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


@method_decorator(never_cache, name="get")
class EditSpendingRequestView(
    HardLoginRequiredMixin, GlobalOrObjectPermissionRequiredMixin, UpdateView
):
    model = SpendingRequest
    permission_required = ("donations.change_spendingrequest",)
    form_class = forms.SpendingRequestEditForm
    template_name = "donations/edit_spending_request.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse("manage_spending_request", args=(self.object.pk,))

    def dispatch(self, request, *args, **kwargs):
        if not self.get_object().editable:
            messages.add_message(
                self.request,
                messages.INFO,
                "Il n'est plus possible d'éditer cette demande de dépense.",
            )
            return reverse("manage_spending_request", args=(self.object.pk,))

        return super().dispatch(request, *args, **kwargs)

    def render_to_response(self, context, **response_kwargs):
        if self.object.edition_message:
            messages.add_message(
                self.request,
                messages.WARNING,
                self.object.edition_message,
            )
        return super().render_to_response(self.get_context_data(), **response_kwargs)

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            spending_request=self.object,
            supportgroup=self.object.group,
            **kwargs,
        )


class DeleteSpendingRequestView(
    HardLoginRequiredMixin, GlobalOrObjectPermissionRequiredMixin, DeleteView
):
    model = SpendingRequest
    permission_required = ("donations.delete_spendingrequest",)

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object.deletable:
            messages.add_message(
                self.request,
                messages.INFO,
                "Il n'est plus possible de supprimer cette demande de dépense",
            )
            return HttpResponseRedirect(
                reverse("manage_spending_request", args=(self.object.pk,))
            )

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        messages.add_message(
            self.request,
            messages.SUCCESS,
            "La demande de dépense a bien été supprimée",
        )
        return reverse("view_group_settings_finance", args=(self.object.group.pk,))


@method_decorator(never_cache, name="get")
class CreateDocumentView(
    HardLoginRequiredMixin, GlobalOrObjectPermissionRequiredMixin, CreateView
):
    model = Document
    form_class = DocumentForm
    permission_required = ("donations.change_spendingrequest",)
    template_name = "donations/create_document.html"
    spending_request = None

    def dispatch(self, request, *args, spending_request_id=None, **kwargs):
        self.spending_request = get_object_or_404(
            SpendingRequest, pk=spending_request_id
        )
        return super().dispatch(request, *args, **kwargs)

    def get_permission_object(self):
        return self.spending_request

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["spending_request"] = self.spending_request
        kwargs["user"] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse("manage_spending_request", args=(self.spending_request.pk,))

    def render_to_response(self, context, **response_kwargs):
        if self.spending_request.edition_message:
            messages.add_message(
                self.request,
                messages.WARNING,
                self.spending_request.edition_message,
            )
        return super().render_to_response(self.get_context_data(), **response_kwargs)

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            spending_request=self.spending_request,
            supportgroup=self.spending_request.group,
            **kwargs,
        )


class AccessDocumentMixin(
    HardLoginRequiredMixin, GlobalOrObjectPermissionRequiredMixin
):
    permission_required = ("donations.change_spendingrequest",)

    def dispatch(self, request, *args, spending_request_id=None, pk=None, **kwargs):
        self.spending_request = get_object_or_404(
            SpendingRequest,
            pk=spending_request_id,
            document__pk=pk,
        )
        return super().dispatch(request, *args, **kwargs)

    def get_permission_object(self):
        return self.spending_request

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            spending_request=self.spending_request,
            supportgroup=self.spending_request.group,
            **kwargs,
        )


@method_decorator(never_cache, name="get")
class EditDocumentView(AccessDocumentMixin, UpdateView):
    model = Document
    queryset = Document.objects.filter(deleted=False)
    form_class = DocumentForm
    template_name = "donations/edit_document.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse("manage_spending_request", args=(self.spending_request.pk,))

    def render_to_response(self, context, **response_kwargs):
        if self.spending_request.edition_message:
            messages.add_message(
                self.request,
                messages.WARNING,
                self.spending_request.edition_message,
            )

        return super().render_to_response(self.get_context_data(), **response_kwargs)


class DeleteDocumentView(AccessDocumentMixin, SingleObjectMixin, View):
    model = Document

    def post(self, request, *args, **kwargs):
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
