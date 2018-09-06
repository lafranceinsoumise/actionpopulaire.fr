from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.views.generic import UpdateView, DeleteView, TemplateView

from agir.authentication.view_mixins import SoftLoginRequiredMixin, HardLoginRequiredMixin
from agir.people.forms import MessagePreferencesForm, AddEmailForm
from agir.people.models import Person


class MessagePreferencesView(SoftLoginRequiredMixin, UpdateView):
    template_name = 'people/message_preferences.html'
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
    template_name = 'people/delete_account.html'

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
    template_name = 'people/email_management.html'
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
    template_name = 'people/confirm_email_deletion.html'
    context_object_name = 'email'

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            success_url=self.get_success_url(),
            **kwargs
        )

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
