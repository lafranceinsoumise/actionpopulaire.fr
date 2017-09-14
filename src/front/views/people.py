from random import choice

from django.views.generic import CreateView, UpdateView, TemplateView
from django.views.generic.edit import ModelFormMixin
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _, string_concat
from django.db import transaction

from people.models import Person

from ..view_mixins import SuccessMessageView, LoginRequiredMixin
from ..forms import SimpleSubscriptionForm, OverseasSubscriptionForm, ProfileForm, EmailFormSet, VolunteerForm

__all__ = ["SubscriptionSuccessView", "SimpleSubscriptionView", "OverseasSubscriptionView", "ChangeProfileView",
           "ProfileConfirmationPage", "VolunteerPage"]


actions = {
    "volunteer": [_("Agir"), reverse_lazy("volunteer")],
    "profile": [_("Nous en dire plus sur nous"), reverse_lazy("profile_change")]
}


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


class ChangeProfileView(LoginRequiredMixin, UpdateView):
    template_name = "front/people/profile.html"
    form_class = ProfileForm
    success_url = string_concat(reverse_lazy("confirmation"), "?from=people")

    def get_object(self, queryset=None):
        """Get the current user as the view object"""
        return self.request.user.person


class ProfileConfirmationPage(TemplateView):
    template_name = 'front/people/confirmation.html'

    def get_context_data(self, **kwargs):
        from_page = self.request.GET.get('from')

        other_actions = [info for page, info in actions.items() if page != from_page]
        action_text, action_link = choice(other_actions)

        return super().get_context_data(action_text=action_text, action_link=action_link)


class VolunteerPage(UpdateView):
    template_name = "front/people/profile.html"
    form_class = VolunteerForm
    success_url = string_concat(reverse_lazy("confirmation"), "?from=volunteer")

    def get_object(self, queryset=None):
        """Get the current user as the view object"""
        return self.request.user.person


class OldChangeProfileView(LoginRequiredMixin, ModelFormMixin, TemplateView):
    template_name = "front/people/profile.html"
    form_class = ProfileForm

    def get_email_formset(self):
        """Initialize the email inline formset"""
        kwargs = {}

        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES
            })

        return EmailFormSet(
            instance=self.object,
            **kwargs,
        )

    def get_context_data(self, **kwargs):
        """Add the email inline formset to the context"""

        if 'email_formset' not in kwargs:
            kwargs['email_formset'] = self.get_email_formset()

        return super().get_context_data(
            **kwargs
        )

    def get_object(self, queryset=None):
        """Get the current user as the view object"""
        return self.request.user.person

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating form and formset with the passed
        POST variables and then checked for validity.
        """
        self.object = self.get_object()

        profile_form = self.get_form()
        email_formset = self.get_email_formset()

        if profile_form.is_valid() and email_formset.is_valid():
            return self.both_forms_valid(profile_form, email_formset)
        else:
            # display the forms with errors
            return self.render_to_response(self.get_context_data(form=profile_form, email_formset=email_formset))

    def both_forms_valid(self, profile_form, email_formset):
        """Saves both forms, using an atomic transaction"""
        with transaction.atomic():
            email_formset.save()
            return self.form_valid(profile_form)
