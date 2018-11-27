from django.contrib import messages
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.utils.http import urlquote
from django.utils.translation import ugettext as _
from django.views.generic import UpdateView, DeleteView, TemplateView, FormView

from agir.authentication.view_mixins import (
    SoftLoginRequiredMixin,
    HardLoginRequiredMixin,
)
from agir.authentication.views import RedirectToMixin
from agir.people.forms import (
    InsoumisePreferencesForm,
    AddEmailForm,
    SendValidationSMSForm,
    CodeValidationForm,
    ExternalPersonPreferencesForm,
)
from agir.people.models import Person


class MessagePreferencesView(SoftLoginRequiredMixin, UpdateView):
    template_name = "people/message_preferences.html"
    success_url = reverse_lazy("message_preferences")

    def get_object(self, queryset=None):
        return self.request.user.person

    def get_form_class(self):
        if self.object.is_insoumise:
            return InsoumisePreferencesForm

        return ExternalPersonPreferencesForm

    def get_success_url(self):
        if self.request.POST.get("validation"):
            return reverse("send_validation_sms")
        return super().get_success_url()

    def form_valid(self, form):
        res = super().form_valid(form)

        if getattr(form, "no_mail", False):
            messages.add_message(
                self.request,
                messages.INFO,
                "Vous êtes maintenant désinscrit⋅e de toutes les lettres d'information de la France insoumise.",
            )
        else:
            messages.add_message(
                self.request,
                messages.SUCCESS,
                "Vos préférences ont bien été enregistrées !",
            )

        return res


class DeleteAccountView(HardLoginRequiredMixin, DeleteView):
    template_name = "people/delete_account.html"

    def get_success_url(self):
        return reverse("delete_account_success")

    def get_object(self, queryset=None):
        return self.request.user.person

    def delete(self, request, *args, **kwargs):
        messages.add_message(
            self.request, messages.SUCCESS, "Votre compte a bien été supprimé !"
        )
        response = super().delete(request, *args, **kwargs)
        logout(self.request)

        return response


class EmailManagementView(HardLoginRequiredMixin, TemplateView):
    template_name = "people/email_management.html"
    queryset = Person.objects.all()

    def get_object(self):
        return self.request.user.person

    def get_add_email_form(self):
        kwargs = {}

        if self.request.method in ("POST", "PUT"):
            kwargs.update({"data": self.request.POST, "files": self.request.FILES})

        return AddEmailForm(person=self.object, **kwargs)

    def get_context_data(self, **kwargs):
        emails = self.object.emails.all()

        kwargs.update(
            {"person": self.object, "emails": emails, "can_delete": len(emails) > 1}
        )

        kwargs.setdefault("add_email_form", self.get_add_email_form())

        return super().get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        add_email_form = self.get_add_email_form()

        if add_email_form.is_valid():
            add_email_form.save()
            return HttpResponseRedirect(reverse("email_management"))
        else:
            context = self.get_context_data(add_email_form=add_email_form)
            return self.render_to_response(context)


class DeleteEmailAddressView(HardLoginRequiredMixin, DeleteView):
    success_url = reverse_lazy("email_management")
    template_name = "people/confirm_email_deletion.html"
    context_object_name = "email"

    def get_context_data(self, **kwargs):
        return super().get_context_data(success_url=self.get_success_url(), **kwargs)

    def get_queryset(self):
        return self.request.user.person.emails.all()

    def get(self, request, *args, **kwargs):
        if len(self.get_queryset()) <= 1:
            return HttpResponseRedirect(self.success_url)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if len(self.get_queryset()) <= 1:
            return HttpResponseRedirect(self.success_url)
        return super().post(request, *args, **kwargs)


class RedirectAlreadyValidatedPeopleMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.person.contact_phone_status == Person.CONTACT_PHONE_VERIFIED:
            messages.add_message(
                request, messages.SUCCESS, _("Votre numéro a déjà été validé.")
            )
            return HttpResponseRedirect(reverse("message_preferences"))
        elif request.user.person.contact_phone_status == Person.CONTACT_PHONE_PENDING:
            messages.add_message(
                request,
                messages.INFO,
                _(
                    "Votre numéro était déjà validé par une autre personne et est en attente de validation manuelle."
                ),
            )

        return super().dispatch(request, *args, **kwargs)


class SendValidationSMSView(
    HardLoginRequiredMixin,
    RedirectAlreadyValidatedPeopleMixin,
    RedirectToMixin,
    UpdateView,
):
    form_class = SendValidationSMSForm
    template_name = "people/send_validation_sms.html"

    def get_object(self, queryset=None):
        return self.request.user.person

    def get_success_url(self):
        success_url = reverse_lazy("sms_code_validation")
        redirect_to = self.get_redirect_url()
        if redirect_to:
            success_url += f"?{self.redirect_field_name}={urlquote(redirect_to)}"

        return success_url

    def form_valid(self, form):
        code = form.send_code(self.request)

        if code is None:
            return super().form_invalid(form)

        messages.add_message(self.request, messages.DEBUG, f"Le code envoyé est {code}")
        return super().form_valid(form)


class CodeValidationView(
    HardLoginRequiredMixin,
    RedirectAlreadyValidatedPeopleMixin,
    RedirectToMixin,
    FormView,
):
    form_class = CodeValidationForm
    template_name = "people/send_validation_sms.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["person"] = self.request.user.person

        return kwargs

    def get_success_url(self):
        return self.get_redirect_url() or reverse_lazy("message_preferences")

    def form_valid(self, form):
        person = self.request.user.person

        if Person.objects.filter(
            contact_phone=person.contact_phone,
            contact_phone_status=Person.CONTACT_PHONE_VERIFIED,
        ).exists():
            person.contact_phone_status = Person.CONTACT_PHONE_PENDING
            messages.add_message(
                self.request,
                messages.INFO,
                _(
                    "Ce numéro est déjà utilisé par une autre personne : vous êtes en attente de validation manuelle."
                ),
            )
        else:
            person.contact_phone_status = Person.CONTACT_PHONE_VERIFIED
            messages.add_message(
                self.request,
                messages.INFO,
                _("Votre numéro a été correctement validé."),
            )

        person.save()
        return super().form_valid(form)
