from django.views.generic import CreateView, UpdateView, TemplateView
from django.views.generic.edit import FormView
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib import messages

from people.models import Person

from ..view_mixins import SoftLoginRequiredMixin, SimpleOpengraphMixin
from ..forms import (
    SimpleSubscriptionForm, OverseasSubscriptionForm, ProfileForm,
    VolunteerForm, MessagePreferencesForm, UnsubscribeForm
)

__all__ = ["SubscriptionSuccessView", "SimpleSubscriptionView", "OverseasSubscriptionView", "ChangeProfileView",
           "ChangeProfileConfirmationView", "VolunteerView", "VolunteerConfirmationView", "MessagePreferencesView",
           "UnsubscribeView", "UnsubscribeSuccessView"]


class UnsubscribeSuccessView(TemplateView):
    template_name = "front/people/unsubscribe_success.html"


class UnsubscribeView(SimpleOpengraphMixin, FormView):
    template_name = "front/people/unsubscribe.html"
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
    template_name = "front/people/confirmation_subscription.html"


class SimpleSubscriptionView(SimpleOpengraphMixin, CreateView):
    template_name = "front/people/simple_subscription.html"
    success_url = reverse_lazy('subscription_success')
    model = Person
    form_class = SimpleSubscriptionForm

    meta_title = "Rejoignez la France insoumise"
    meta_description = "Rejoignez la France insoumise sur lafranceinsoumise.fr"


class OverseasSubscriptionView(SimpleOpengraphMixin, CreateView):
    template_name = "front/people/overseas_subscription.html"
    success_url = reverse_lazy('subscription_success')
    model = Person
    form_class = OverseasSubscriptionForm

    meta_title = "Rejoignez la France insoumise"
    meta_description = "Rejoignez la France insoumise sur lafranceinsoumise.fr"


class ChangeProfileView(SoftLoginRequiredMixin, UpdateView):
    template_name = "front/people/profile.html"
    form_class = ProfileForm
    success_url = reverse_lazy("confirmation_profile")

    def get_object(self, queryset=None):
        """Get the current user as the view object"""
        return self.request.user.person


class ChangeProfileConfirmationView(SimpleOpengraphMixin, TemplateView):
    template_name = 'front/people/confirmation_profile.html'


class VolunteerView(SoftLoginRequiredMixin, UpdateView):
    template_name = "front/people/volunteer.html"
    form_class = VolunteerForm
    success_url = reverse_lazy("confirmation_volunteer")

    def get_object(self, queryset=None):
        """Get the current user as the view object"""
        return self.request.user.person


class VolunteerConfirmationView(TemplateView):
    template_name = 'front/people/confirmation_volunteer.html'


class MessagePreferencesView(SoftLoginRequiredMixin, UpdateView):
    template_name = 'front/people/message_preferences.html'
    form_class = MessagePreferencesForm

    # in case one is not connected, redirect to the unlogged unsubscribe page
    unlogged_redirect_url = 'unsubscribe'

    def get_object(self, queryset=None):
        return self.request.user.person

    def form_valid(self, form):
        res = super().form_valid(form)

        messages.add_message(
            self.request,
            messages.SUCCESS,
            "Vos préférences ont bien été enregistrées !"
        )

        return res
