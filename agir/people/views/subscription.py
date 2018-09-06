from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView, TemplateView, CreateView

from agir.front.view_mixins import SimpleOpengraphMixin
from agir.people.forms import UnsubscribeForm, SimpleSubscriptionForm, OverseasSubscriptionForm
from agir.people.models import Person


class UnsubscribeView(SimpleOpengraphMixin, FormView):
    template_name = "people/unsubscribe.html"
    success_url = reverse_lazy('unsubscribe_success')
    form_class = UnsubscribeForm

    meta_title = "Ne plus recevoir de emails"
    meta_description = "Désabonnez-vous des emails de la France insoumise"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('message_preferences'))
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        form.unsubscribe()
        return super().form_valid(form)


class SubscriptionSuccessView(TemplateView):
    template_name = "people/confirmation_subscription.html"


class SimpleSubscriptionView(SimpleOpengraphMixin, CreateView):
    template_name = "people/simple_subscription.html"
    success_url = reverse_lazy('subscription_success')
    model = Person
    form_class = SimpleSubscriptionForm

    meta_title = "Rejoignez la France insoumise"
    meta_description = "Rejoignez la France insoumise sur lafranceinsoumise.fr"


class OverseasSubscriptionView(SimpleOpengraphMixin, CreateView):
    template_name = "people/overseas_subscription.html"
    success_url = reverse_lazy('subscription_success')
    model = Person
    form_class = OverseasSubscriptionForm

    meta_title = "Rejoignez la France insoumise"
    meta_description = "Rejoignez la France insoumise sur lafranceinsoumise.fr"

