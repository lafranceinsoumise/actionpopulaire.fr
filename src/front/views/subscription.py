from django.views.generic import CreateView
from django.core.urlresolvers import reverse_lazy

from people.models import Person

from ..view_mixins import SuccessMessageView
from ..forms import SimpleSubscriptionForm, OverseasSubscriptionForm

__all__ = ["SubscriptionSuccessView", "SimpleSubscriptionView", "OverseasSubscriptionView"]


class SubscriptionSuccessView(SuccessMessageView):
    title = "Merci de votre appui"
    message = """
    Votre soutien est bien enregistré. Vous serez tenu au courant de l'actualité du mouvement.
    """


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
