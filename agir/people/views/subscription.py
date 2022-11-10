from django.contrib import messages
from django.db import IntegrityError, transaction
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.generic import FormView

from agir.authentication.tokens import subscription_confirmation_token_generator
from agir.authentication.utils import hard_login
from agir.front.view_mixins import SimpleOpengraphMixin
from agir.lib.tasks import geocode_person
from agir.people.actions.subscription import (
    SUBSCRIPTION_TYPE_LFI,
    SUBSCRIPTIONS_EMAILS,
    subscription_success_redirect_url,
    save_subscription_information,
)
from agir.people.forms import AnonymousUnsubscribeForm
from agir.people.models import Person


@method_decorator(never_cache, name="get")
class UnsubscribeView(SimpleOpengraphMixin, FormView):
    template_name = "people/unsubscribe.html"
    success_url = reverse_lazy("unsubscribe_success")
    form_class = AnonymousUnsubscribeForm

    meta_title = "Ne plus recevoir de emails"
    meta_description = "Désabonnez-vous des emails de la France insoumise"

    def get_success_url(self):
        if not self.request.user.is_authenticated or self.request.user.person is None:
            return self.success_url

        messages.add_message(
            self.request,
            messages.INFO,
            "Vous êtes maintenant désinscrit⋅e de toutes les lettres d'information.",
        )
        return reverse_lazy("contact")

    def form_valid(self, form):
        form.unsubscribe()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            email=self.request.user.person.email
            if self.request.user.is_authenticated
            else None,
            **kwargs,
        )


class ConfirmSubscriptionView(View):
    """Vue prenant en charge l'URL de confirmation d'inscription

    Cette URL est envoyée par email grâce à la tâche :py:class:`agir.people.tasks.send_confirmation_email`
    """

    response_class = TemplateResponse
    error_template = "people/confirmation_mail_error.html"
    error_messages = {
        "invalid": _(
            "Il semble que celui-ci est invalide. Avez-vous bien cliqué sur le bouton, ou copié la totalité du lien ?"
        ),
        "expired": _("Il semble que celui-ci est expiré."),
        "already_created": "Votre inscription était déjà confirmée.",
    }
    allowed_fields = [
        "email",
        "location_zip",
        "location_address1",
        "location_address2",
        "location_city",
        "location_country",
        "contact_phone",
        "first_name",
        "last_name",
        "contact_phone",
        "type",
        "referer",
        "referrer",
        "mandat",
        "android",
        "ios",
        "next",
    ]
    show_already_created_message = True
    default_type = SUBSCRIPTION_TYPE_LFI

    @never_cache
    def get(self, request, *args, **kwargs):
        params = request.GET.dict()

        if "email" not in params or "token" not in params:
            return self.error_page(message=self.error_messages["invalid"])

        token = params.pop("token")

        if not all(p in self.allowed_fields or p.startswith("meta_") for p in params):
            return self.error_page(self.error_messages["invalid"])

        if not subscription_confirmation_token_generator.check_token(token, **params):
            return self.error_page(self.error_messages["expired"])

        self.type = params.pop("type", self.default_type)

        self.perform_create(params)
        return self.success_page(params)

    def error_page(self, message):
        return self.render(
            self.error_template,
            {
                "message": message,
                "show_retry": self.default_type == SUBSCRIPTION_TYPE_LFI,
            },
        )

    def perform_create(self, params):
        with transaction.atomic():
            try:
                # double transaction sinon la transaction externe n'est plus utilisable après l'exception
                with transaction.atomic():
                    self.person = Person.objects.create_person(params["email"])
                    already_created = False
            except IntegrityError:
                self.person = Person.objects.get_by_natural_key(params["email"])
                already_created = True

            metadata = {}
            for p in list(params):
                if p.startswith("meta_"):
                    metadata[p[len("meta_") :]] = params.pop(p)

            if metadata:
                params["metadata"] = metadata

            save_subscription_information(self.person, self.type, params, new=True)

        if already_created and self.show_already_created_message:
            messages.add_message(
                self.request, messages.INFO, self.error_messages["already_created"]
            )
        elif not already_created and "welcome" in SUBSCRIPTIONS_EMAILS[self.type]:
            from ..tasks import send_welcome_mail

            send_welcome_mail.delay(self.person.pk, type=self.type)

        hard_login(self.request, self.person)

        if self.person.coordinates_type is None:
            geocode_person.delay(self.person.pk)

    def render(self, template, context=None, **kwargs):
        if context is None:
            context = {}

        return self.response_class(
            request=self.request, template=[template], context=context, **kwargs
        )

    def success_page(self, params):
        return HttpResponseRedirect(
            subscription_success_redirect_url(self.type, self.person.id, params)
        )
