from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import FormView, TemplateView
from django.utils.translation import ugettext_lazy as _

from agir.authentication.utils import soft_login
from agir.front.view_mixins import SimpleOpengraphMixin
from agir.people.forms import (
    AnonymousUnsubscribeForm,
    SimpleSubscriptionForm,
    OverseasSubscriptionForm,
)
from agir.people.models import Person
from agir.authentication.subscription import subscription_confirmation_token_generator
from agir.people.tasks import send_welcome_mail
from agir.people.token_buckets import (
    SubscribeIPBucket,
    SubscribeEmailBucket,
    is_rate_limited_for_subscription,
)


class UnsubscribeView(SimpleOpengraphMixin, FormView):
    template_name = "people/unsubscribe.html"
    success_url = reverse_lazy("unsubscribe_success")
    form_class = AnonymousUnsubscribeForm

    meta_title = "Ne plus recevoir de emails"
    meta_description = "Désabonnez-vous des emails de la France insoumise"

    def form_valid(self, form):
        form.unsubscribe()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            email=self.request.user.person.email
            if self.request.user.is_authenticated
            else None,
            **kwargs
        )


class ConfirmationMailSentView(TemplateView):
    template_name = "people/confirmation_mail_sent.html"


def subscription_rate_limite_message(args):
    pass


class BaseSubscriptionView(SimpleOpengraphMixin, FormView):
    success_url = reverse_lazy("subscription_mail_sent")
    meta_title = "Rejoignez la France insoumise"
    meta_description = "Rejoignez la France insoumise sur lafranceinsoumise.fr"

    def form_valid(self, form):
        if is_rate_limited_for_subscription(
            ip=self.request.META["REMOTE_ADDR"], email=form.cleaned_data["email"]
        ):
            form.add_error(
                field=None, error=ValidationError(subscription_rate_limite_message)
            )
            return self.form_invalid(form)

        form.send_confirmation_email()
        return super().form_valid(form)


class SimpleSubscriptionView(BaseSubscriptionView):
    template_name = "people/simple_subscription.html"
    form_class = SimpleSubscriptionForm


class OverseasSubscriptionView(BaseSubscriptionView):
    template_name = "people/overseas_subscription.html"
    form_class = OverseasSubscriptionForm


class ConfirmSubscriptionView(View):
    response_class = TemplateResponse
    success_template = "people/confirmation_subscription.html"
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
        "location_contry",
    ]

    def get(self, request, *args, **kwargs):
        params = request.GET.dict()

        if "email" not in params or "token" not in params:
            return self.error_page(message=self.error_messages["invalid"])

        token = params.pop("token")

        if not set(params).issubset(self.allowed_fields):
            return self.error_page(self.error_messages["invalid"])

        if not subscription_confirmation_token_generator.check_token(token, **params):
            return self.error_page(self.error_messages["expired"])

        self.perform_create(params)
        return self.success_page()

    def error_page(self, message):
        return self.render(self.error_template, {"message": message})

    def success_page(self):
        return self.render(self.success_template)

    def perform_create(self, params):
        try:
            self.person = Person.objects.get_by_natural_key(params["email"])
            messages.add_message(
                self.request, messages.INFO, self.error_messages["already_created"]
            )
        except Person.DoesNotExist:
            self.person = Person.objects.create_person(**params)
            send_welcome_mail.delay(self.person.pk)

        soft_login(self.request, self.person)

    def render(self, template, context=None, **kwargs):
        if context is None:
            context = {}

        return self.response_class(
            request=self.request, template=[template], context=context, **kwargs
        )
