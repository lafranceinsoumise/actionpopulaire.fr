from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import UpdateView, DetailView

from agir.authentication.view_mixins import SoftLoginRequiredMixin
from agir.people import tasks
from agir.people.actions.person_forms import get_people_form_class
from agir.people.models import PersonForm, PersonFormSubmission


class PeopleFormView(SoftLoginRequiredMixin, UpdateView):
    queryset = PersonForm.objects.published()
    template_name = 'people/person_form.html'

    def get_success_url(self):
        return reverse('person_form_confirmation', args=(self.person_form_instance.slug,))

    def get_object(self, queryset=None):
        return self.request.user.person

    def get_person_form_instance(self):
        try:
            return self.get_queryset().get(slug=self.kwargs['slug'])
        except PersonForm.DoesNotExist:
            raise Http404("Ce formulaire n'existe pas.")

    def get_form_class(self):
        return get_people_form_class(self.person_form_instance)

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            person_form=self.person_form_instance,
            is_authorized=self.person_form_instance.is_authorized(self.object)
        )

    def get(self, request, *args, **kwargs):
        self.person_form_instance = self.get_person_form_instance()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.person_form_instance = self.get_person_form_instance()
        if not self.person_form_instance.is_open or \
                not self.person_form_instance.is_authorized(self.request.user.person):
            return self.get(request, *args, **kwargs)
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        r = super().form_valid(form)
        if self.person_form_instance.send_confirmation:
            tasks.send_person_form_confirmation.delay(form.submission.pk)
        if self.person_form_instance.send_answers_to:
            tasks.send_person_form_notification.delay(form.submission.pk)

        return r


class PeopleFormEditSubmissionView(PeopleFormView):
    def get_form_kwargs(self):
        if self.person_form_instance.editable == False:
            raise Http404()

        kwargs = super().get_form_kwargs()
        kwargs['submission'] = get_object_or_404(PersonFormSubmission, pk=self.kwargs['pk'])

        return kwargs


class PeopleFormConfirmationView(DetailView):
    template_name = 'people/person_form_confirmation.html'
    queryset = PersonForm.objects.filter(published=True)

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            person_form=self.object
        )
