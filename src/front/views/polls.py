from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import TemplateView, FormView
from django.views.generic.detail import SingleObjectMixin

from front.forms.polls import PollParticipationForm
from front.view_mixins import SoftLoginRequiredMixin
from polls.models import Poll, PollChoice

__all__ = ['PollParticipationView', 'PollConfirmationView', 'PollFinishedView']


class PollParticipationView(SoftLoginRequiredMixin, SingleObjectMixin, FormView):
    template_name = "front/polls/detail.html"
    context_object_name = 'poll'
    form_class = PollParticipationForm
    success_url = reverse_lazy('confirmation_poll')
    queryset = Poll.objects.filter(start__lt=timezone.now())

    def get_form_kwargs(self):
        return {'poll': self.object, **super().get_form_kwargs()}

    def get(self, *args, **kwargs):
        self.object = self.get_object()
        if self.object.end < timezone.now():
            return redirect('finished_poll')
        if PollChoice.objects.filter(person=self.request.user.person, poll=self.object).exists():
            raise PermissionDenied('Vous avez déjà participé !')

        return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        self.object = self.get_object()
        if self.request.user.person.created > self.object.start:
            raise PermissionDenied('Vous vous êtes inscrit⋅e trop récemment pour participer.')
        if PollChoice.objects.filter(person=self.request.user.person, poll=self.object).exists():
            raise PermissionDenied('Vous avez déjà participé !')

        return super().post(*args, **kwargs)

    def form_valid(self, form):
        form.make_choice(self.request.user)
        return super().form_valid(form)


class PollConfirmationView(TemplateView):
    template_name = "front/polls/confirmation.html"


class PollFinishedView(TemplateView):
    template_name = "front/polls/finished.html"
