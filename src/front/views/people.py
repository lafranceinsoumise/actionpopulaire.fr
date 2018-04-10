from django.conf import settings
from django.contrib.auth import logout
from django.views.generic import CreateView, UpdateView, TemplateView, DeleteView, DetailView
from django.views.generic.edit import FormView
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib import messages

from people.models import Person, PersonForm

from ..view_mixins import SoftLoginRequiredMixin, HardLoginRequiredMixin, SimpleOpengraphMixin
from ..forms import (
    SimpleSubscriptionForm, OverseasSubscriptionForm, ProfileForm,
    VolunteerForm, MessagePreferencesForm, UnsubscribeForm, AddEmailForm, get_people_form_class
)

__all__ = ['SubscriptionSuccessView', 'SimpleSubscriptionView', 'OverseasSubscriptionView', 'ChangeProfileView',
           'ChangeProfileConfirmationView', 'VolunteerView', 'VolunteerConfirmationView', 'MessagePreferencesView',
           'UnsubscribeView', 'DeleteAccountView', 'EmailManagementView', 'DeleteEmailAddressView',
           'PeopleFormView', 'PeopleFormConfirmationView']


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
    success_url = reverse_lazy('message_preferences')

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


class DeleteAccountView(HardLoginRequiredMixin, DeleteView):
    template_name = 'front/people/delete_account.html'

    def get_success_url(self):
        return f"{settings.OAUTH['logoff_url']}?next={reverse('delete_account_success')}"

    def get_object(self, queryset=None):
        return self.request.user.person

    def delete(self, request, *args, **kwargs):
        messages.add_message(
            self.request,
            messages.SUCCESS,
            "Votre compte a bien été supprimé !"
        )
        response = super().delete(request, *args, **kwargs)
        logout(self.request)

        return response


class EmailManagementView(HardLoginRequiredMixin, TemplateView):
    template_name = 'front/people/email_management.html'
    queryset = Person.objects.all()

    def get_object(self):
        return self.request.user.person

    def get_add_email_form(self):
        kwargs = {}

        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })

        return AddEmailForm(
            person=self.object,
            **kwargs
        )

    def get_context_data(self, **kwargs):
        emails = self.object.emails.all()

        kwargs.update({
            'person': self.object,
            'emails': emails,
            'can_delete': len(emails) > 1
        })

        kwargs.setdefault('add_email_form',  self.get_add_email_form())

        return super().get_context_data(
            **kwargs
        )

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        add_email_form = self.get_add_email_form()

        if add_email_form.is_valid():
            add_email_form.save()
            return HttpResponseRedirect(reverse("email_management"))
        else:
            context = self.get_context_data(add_email_form=add_email_form)
            return self.render_to_response(context)


class DeleteEmailAddressView(HardLoginRequiredMixin, DeleteView):
    success_url = reverse_lazy('email_management')
    template_name = 'front/people/confirm_email_deletion.html'
    context_object_name = 'email'

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            success_url=self.get_success_url(),
            **kwargs
        )

    def get_queryset(self):
        return self.request.user.person.emails.all()

    def dispatch(self, request, *args, **kwargs):
        if len(self.get_queryset()) <= 1:
            return HttpResponseForbidden(b'forbidden')
        return super().dispatch(request, *args, **kwargs)


class PeopleFormView(SoftLoginRequiredMixin, UpdateView):
    queryset = PersonForm.objects.filter(published=True)
    template_name = 'front/people/person_form.html'

    def get_success_url(self):
        return reverse('person_form_confirmation', args=(self.person_form.slug,))

    def get_object(self, queryset=None):
        return self.request.user.person

    def get_person_form_instance(self):
        try:
            return self.get_queryset().get(slug=self.kwargs['slug'])
        except PersonForm.DoesNotExist:
            raise Http404("Formulaire does not exist")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['person'] = self.object
        return kwargs

    def get_form_class(self):
        return get_people_form_class(self.person_form)

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            person_form=self.person_form
        )

    def get(self, request, *args, **kwargs):
        self.person_form = self.get_person_form_instance()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.person_form = self.get_person_form_instance()
        return super().post(request, *args, **kwargs)


class PeopleFormConfirmationView(DetailView):
    template_name = 'front/people/person_form_confirmation.html'
    queryset = PersonForm.objects.filter(published=True)

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            person_form=self.object
        )
