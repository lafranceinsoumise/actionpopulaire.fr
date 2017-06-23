from django.views.generic import TemplateView, FormView, CreateView
from django.core.urlresolvers import reverse_lazy

from people.models import Person

from .forms import SimpleSubscriptionForm, OverseasSubscriptionForm


class SubscriptionSuccessView(TemplateView):
    template_name = "front/subscription_success.html"


class SimpleSubscriptionView(CreateView):
    template_name = "front/simple_subscription.html"
    success_url = reverse_lazy('subscription_success')
    model = Person
    form_class = SimpleSubscriptionForm


class OverseasSubscriptionView(CreateView):
    template_name = "front/overseas_subscription.html"
    success_url = reverse_lazy('subscription_success')
    model = Person
    form_class = OverseasSubscriptionForm