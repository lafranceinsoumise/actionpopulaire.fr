from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import TemplateView, FormView
from django.views.generic.detail import SingleObjectMixin
from django.contrib import messages
from django.utils.translation import ugettext as _

from front.forms.polls import PollParticipationForm
from front.view_mixins import SoftLoginRequiredMixin
from polls.models import Poll, PollChoice

__all__ = ['PollParticipationView', 'PollConfirmationView', 'PollFinishedView']


class PollParticipationView(SoftLoginRequiredMixin, SingleObjectMixin, FormView):
    template_name = "front/polls/detail.html"
    context_object_name = 'poll'
    form_class = PollParticipationForm
    queryset = Poll.objects.filter(start__lt=timezone.now())

    def get_success_url(self):
        return reverse_lazy('participate_poll', args=[self.object.pk])

    def get_form_kwargs(self):
        return {'poll': self.object, **super().get_form_kwargs()}

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            already_voted=PollChoice.objects.filter(person=self.request.user.person, poll=self.object).exists(),
            **kwargs
        )

    def get(self, *args, **kwargs):
        self.object = self.get_object()
        if self.object.end < timezone.now():
            return redirect('finished_poll')

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
        messages.add_message(
            self.request,
            messages.SUCCESS,
            _("Votre choix a bien été pris en compte. Merci d'avoir participé à cette consultation !")
        )
        return super().form_valid(form)


class PollConfirmationView(TemplateView):
    template_name = "front/polls/confirmation.html"


class PollFinishedView(TemplateView):
    template_name = "front/polls/finished.html"
