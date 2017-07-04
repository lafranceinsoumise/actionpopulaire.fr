from django.utils.translation import ugettext as _
from django.views.generic import TemplateView, FormView, CreateView, UpdateView
from django.core.urlresolvers import reverse_lazy

from people.models import Person
from events.models import Event, Calendar

from .forms import SimpleSubscriptionForm, OverseasSubscriptionForm, EventForm
from .view_mixins import SuccessMessageView


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


class CreateEventView(CreateView):
    template_name = "front/event_form.html"
    success_url = reverse_lazy("create_event_success")
    model = Event
    form_class = EventForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Publiez votre événement')
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['calendar'] = Calendar.objects.get(label='evenements_locaux')
        return kwargs


class UpdateEventView(UpdateView):
    template_name = "front/event_form.html"
    success_url = reverse_lazy("update_event_success")
    model = Event
    form_class = EventForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Modifiez votre événement')
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['calendar'] = self.object.calendar
        return kwargs


class CreateEventSuccessView(SuccessMessageView):
    title = "Votre événement a bien été créé"
    message = """
    Vous allez recevoir un mail vous permettant d'administrer votre nouvel événement.
    """


class UpdateEventSuccessView(SuccessMessageView):
    title = "Votre événement a été mis à jour"
    message = """
    Vous allez recevoir un mail vous permettant d'administrer votre nouvel événement.
    """
