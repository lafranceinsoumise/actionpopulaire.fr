from uuid import UUID

from django.contrib import messages
from django.db import IntegrityError
from django.db.models import Case, When, Q, F, Value, CharField
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.utils.http import urlquote
from django.utils.translation import ugettext as _
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.generic import UpdateView, DeleteView, FormView

from agir.authentication.tokens import add_email_confirmation_token_generator
from agir.authentication.utils import hard_login
from agir.authentication.view_mixins import (
    SoftLoginRequiredMixin,
    HardLoginRequiredMixin,
)
from agir.authentication.views import RedirectToMixin
from agir.elus.models import types_elus, MandatMunicipal
from agir.people.forms import (
    SendValidationSMSForm,
    CodeValidationForm,
    MembreReseauElusForm,
)
from agir.people.models import Person


class ConfirmChangeMailView(View):
    """
    Confirme et enregistre une nouvelle adresse email.

    Cette vue peut être atteinte depuis n'importe quel navigateur donc pas besoin d'être connecté.
    Elle vérifie l'integriter du mail + user_pk + token
    Elle redirige vers la vue `profile_contact` en cas de succès
    En cas de problème vérification du token une page est affiché explicant le problème: `invalid`, `expiration`
    """

    success_url = reverse_lazy("contact")
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


class DeleteEmailAddressView(HardLoginRequiredMixin, DeleteView):
    success_url = reverse_lazy("contact")
    template_name = "people/profile/confirm_email_deletion.html"
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


class RedirectAlreadyValidatedPeopleMixin(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.person.contact_phone_status == Person.CONTACT_PHONE_VERIFIED:
            messages.add_message(
                request, messages.SUCCESS, _("Votre numéro a déjà été validé.")
            )
            return HttpResponseRedirect(reverse("contact"))
        elif request.user.person.contact_phone_status == Person.CONTACT_PHONE_PENDING:
            messages.add_message(
                request,
                messages.INFO,
                _(
                    "Votre numéro était déjà validé par une autre personne et est en attente de validation manuelle."
                ),
            )

        return super().dispatch(request, *args, **kwargs)


@method_decorator(never_cache, name="get")
class SendValidationSMSView(
    SoftLoginRequiredMixin,
    RedirectAlreadyValidatedPeopleMixin,
    RedirectToMixin,
    UpdateView,
):
    form_class = SendValidationSMSForm
    template_name = "people/profile/send_validation_sms.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

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


@method_decorator(never_cache, name="get")
class CodeValidationView(
    SoftLoginRequiredMixin,
    RedirectAlreadyValidatedPeopleMixin,
    RedirectToMixin,
    FormView,
):
    form_class = CodeValidationForm
    template_name = "people/profile/send_validation_sms.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["person"] = self.request.user.person

        return kwargs

    def get_success_url(self):
        return self.get_redirect_url() or reverse_lazy("contact")

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


@method_decorator(never_cache, name="get")
class MandatsView(SoftLoginRequiredMixin, UpdateView):
    template_name = "people/profile/mandats.html"
    form_class = MembreReseauElusForm
    success_url = reverse_lazy("mandats")

    def get_object(self, queryset=None):
        return self.request.user.person

    def get_context_data(self, **kwargs):
        person = self.request.user.person

        mandats = []
        for type, model in types_elus.items():
            qs = model.objects.filter(person=person)
            if type == "municipal":
                qs = qs.annotate(
                    epci=Case(
                        When(
                            ~Q(communautaire=MandatMunicipal.MANDAT_EPCI_PAS_DE_MANDAT),
                            then=F("conseil__epci__nom"),
                        ),
                        default=None,
                        output_field=CharField(),
                    )
                )
            else:
                qs = qs.annotate(epci=Value(None, output_field=CharField()))

            mandats.extend(qs)

        if not mandats or person.membre_reseau_elus == Person.MEMBRE_RESEAU_EXCLUS:
            kwargs["form"] = None

        return super().get_context_data(**kwargs, mandats=mandats, person=person,)

    def form_invalid(self, form):
        return super().form_invalid(form)

    def form_valid(self, form):
        messages.add_message(
            request=self.request,
            level=messages.SUCCESS,
            message="Merci, votre choix a été pris en compte",
        )
        return super().form_valid(form)
