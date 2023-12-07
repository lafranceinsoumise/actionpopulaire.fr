from functools import partial

from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, transaction
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView, FormView
from django.views.generic.detail import SingleObjectMixin

from agir.authentication.view_mixins import (
    SoftLoginRequiredMixin,
)
from agir.people.models import Person
from .forms import PollParticipationForm
from .models import Poll, PollChoice

__all__ = ["PollParticipationView", "PollFinishedView"]

from .tasks import send_vote_confirmation_email

from ..lib.http import add_query_params_to_url


@method_decorator(never_cache, name="get")
class PollParticipationView(
    SoftLoginRequiredMixin,
    SingleObjectMixin,
    FormView,
):
    template_name = "polls/detail.html"
    context_object_name = "poll"
    form_class = PollParticipationForm

    def get_queryset(self):
        # use get queryset because timezone.now must be evaluated each time
        return Poll.objects.filter(start__lt=timezone.now())

    def get_form_kwargs(self):
        return {"poll": self.object, **super().get_form_kwargs()}

    def get_context_data(self, **kwargs):
        is_authorized = (
            self.object.authorized_segment is None
            or self.object.authorized_segment.is_included(self.request.user.person)
        )

        if not is_authorized and not self.object.unauthorized_message:
            raise PermissionDenied(
                "Vous n'êtes pas autorisé⋅e à participer à cette consultation."
            )

        poll_choice = PollChoice.objects.filter(
            person=self.request.user.person, poll=self.object
        ).first()

        return super().get_context_data(
            already_voted=(poll_choice is not None),
            anonymous_id=(poll_choice is not None and poll_choice.anonymous_id),
            is_authorized=is_authorized,
            **kwargs
        )

    def get(self, *args, **kwargs):
        self.object = self.get_object()
        if (
            self.object.end < timezone.now()
            and PollChoice.objects.filter(
                person=self.request.user.person, poll=self.object
            ).first()
            is None
        ):
            return redirect("finished_poll")

        if (
            self.object.rules.get("verified_user")
            and self.request.user.person.contact_phone_status
            != Person.CONTACT_PHONE_VERIFIED
        ):
            return redirect_to_login(
                self.request.get_full_path(), reverse_lazy("send_validation_sms")
            )

        return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        self.object = self.get_object()
        if (
            self.object.authorized_segment is not None
            and not self.object.authorized_segment.is_included(self.request.user.person)
        ):
            raise PermissionDenied(
                "Vous n'êtes pas autorisé⋅e à participer à cette consultation."
            )
        if (
            self.object.rules.get("verified_user")
            and self.request.user.person.contact_phone_status
            != Person.CONTACT_PHONE_VERIFIED
        ):
            raise PermissionDenied(
                "Vous devez avoir fait vérifier votre numéro de téléphone pour participer."
            )
        if self.request.user.person.created > self.object.start:
            raise PermissionDenied(
                "Vous vous êtes inscrit⋅e trop récemment pour participer."
            )
        if PollChoice.objects.filter(
            person=self.request.user.person, poll=self.object
        ).exists():
            raise PermissionDenied("Vous avez déjà participé !")

        return super().post(*args, **kwargs)

    def get_success_url(self, choice=None):
        url = reverse_lazy("participate_poll", args=[self.object.pk])

        if self.object.rules.get("success_url"):
            anonymous_id = choice.anonymous_id if choice else None
            url = add_query_params_to_url(
                self.object.rules["success_url"], {"anonymous_id": anonymous_id}
            )

        return url

    def form_valid(self, form):
        try:
            choice = form.make_choice(self.request.user)
        except (
            IntegrityError
        ):  # there probably has been a race condition when POSTing twice
            return HttpResponseRedirect(self.get_success_url())

        if self.object.rules.get("confirmation_email", True):
            transaction.on_commit(
                partial(send_vote_confirmation_email.delay, choice.id)
            )

        messages.add_message(
            self.request,
            messages.SUCCESS,
            _(
                "Votre choix a bien été pris en compte. Merci d'avoir participé à cette consultation !"
            ),
        )

        return HttpResponseRedirect(self.get_success_url(choice))


class PollFinishedView(TemplateView):
    template_name = "polls/finished.html"
