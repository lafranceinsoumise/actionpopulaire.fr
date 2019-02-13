import sys
from uuid import UUID

from django.contrib import messages
from django.contrib.auth import logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse_lazy, reverse
from django.utils.http import urlquote, urlencode
from django.utils.translation import ugettext as _
from django.views import View
from django.views.generic import UpdateView, DeleteView, TemplateView, FormView
from prompt_toolkit.validation import ValidationError

from agir.authentication.subscription import add_email_confirmation_token_generator
from agir.authentication.utils import hard_login
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
    PersonEmail,
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


class ConfirmChangeMail(View):
    """
    Confirme et enregistre une nouvelle adresse email.

    Cette vue peut être atteinte depuis n'importe quel navigateur donc pas besoin d'être connecté.
    Elle vérifie l'integriter du mail + user_pk + token
    Elle redirige vers la vue `message_preferences` en cas de succès
    En cas de problème vérification du token une page est affiché explicant le problème: `invalid`, `expiration`
    """

    success_url = reverse_lazy("message_preferences")
    error_template = "people/confirmation_mail_change_error.html"
    error_messages = {
        "invalid": "Il semble que celui-ci est invalide. Avez-vous bien cliqué sur le bouton, ou copié la totalité du lien ?",
        "expired": "Il semble que celui-ci est expiré.",
        "already_used": "L'adresse {0} est déjà utilisée",
    }

    def error_page(self, key_error, email=""):
        return TemplateResponse(
            self.request,
            [self.error_template],
            context={"message": self.error_messages[key_error].format(email)},
        )

    def get(self, request, **kwargs):
        new_mail = request.GET.get("new_email")
        user_pk = request.GET.get("user")
        token = request.GET.get("token")

        # Check part
        if not new_mail or not user_pk or not token:
            return self.error_page(key_error="invalid")

        try:
            user_pk = str(UUID(user_pk))
        except ValueError:
            return self.error_page(key_error="invalid")

        try:
            self.person = Person.objects.get(pk=user_pk)
        except Person.DoesNotExist:
            return self.error_page(key_error="invalid")

        if add_email_confirmation_token_generator.is_expired(token):
            return self.error_page(key_error="expired")

        params = {"new_email": new_mail, "user": user_pk}
        if not add_email_confirmation_token_generator.check_token(token, **params):
            return self.error_page(key_error="invalid")

        try:
            self.person.add_email(new_mail)
        except IntegrityError:
            return self.error_page(key_error="already_used", email=new_mail)

        # success part
        hard_login(request, self.person)
        self.person.set_primary_email(new_mail)
        messages.add_message(
            self.request,
            messages.SUCCESS,
            "Votre changement de email à été effectué avec succès",
        )

        return HttpResponseRedirect(self.success_url)


class SendConfirmationChangeMail(SoftLoginRequiredMixin, TemplateView):
    template_name = "people/confirmation_change_mail_sent.html"

    def get(self, request):
        self.new_email = request.GET.get("new_email")
        return super().get(request)

    def get_context_data(self, **kwargs):
        return super().get_context_data(new_mail=self.new_email, **kwargs)


class EmailManagementView(SoftLoginRequiredMixin, TemplateView):
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
            new_mail = add_email_form.send_confirmation(self.object.pk)
            if not new_mail:
                context = self.get_context_data(add_email_form=add_email_form)
                return self.render_to_response(context)
            url = reverse("confirmation_change_mail_sent") + "?new_email=" + new_mail
            return HttpResponseRedirect(url)
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
    SoftLoginRequiredMixin,
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
    SoftLoginRequiredMixin,
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
