from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import UpdateView, DetailView
from django.views.generic.list import ListView

from agir.people import tasks
from agir.people.models import PersonForm, PersonFormSubmission, Person
from agir.people.person_forms.actions import get_people_form_class
from agir.people.person_forms.display import (
    get_formatted_submissions,
    get_public_fields,
)


class PeopleFormView(UpdateView):
    queryset = PersonForm.objects.published()
    template_name = "people/person_form.html"

    def get_success_url(self):
        return reverse(
            "person_form_confirmation", args=(self.person_form_instance.slug,)
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["query_params"] = self.request.GET
        return kwargs

    def get_object(self, queryset=None):
        if self.request.user.is_authenticated:
            return self.request.user.person

        return Person()

    def get_person_form_instance(self):
        try:
            return self.get_queryset().get(slug=self.kwargs["slug"])
        except PersonForm.DoesNotExist:
            raise Http404("Ce formulaire n'existe pas.")

    def get_form_class(self):
        return get_people_form_class(self.person_form_instance)

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            person_form=self.person_form_instance,
            is_authorized=self.person_form_instance.is_authorized(self.object),
        )

    def get(self, request, *args, **kwargs):
        self.person_form_instance = self.get_person_form_instance()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.person_form_instance = self.get_person_form_instance()
        if (
            not self.person_form_instance.is_open
            or not self.person_form_instance.is_authorized(self.get_object())
        ):
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
        kwargs["submission"] = get_object_or_404(
            PersonFormSubmission, pk=self.kwargs["pk"]
        )

        if kwargs["submission"].person != self.request.user.person:
            raise PermissionDenied(
                "Impossible de modifier le formulaire de quelqu'un d'autre"
            )

        return kwargs


class PeopleFormConfirmationView(DetailView):
    template_name = "people/person_form_confirmation.html"
    queryset = PersonForm.objects.filter(published=True)

    def get_context_data(self, **kwargs):
        return super().get_context_data(person_form=self.object)


class PeopleFormSubmissionsPublicView(ListView):
    template_name = "people/person_form_public_results.html"
    paginate_by = 20

    def get(self, request, *args, **kwargs):
        try:
            self.person_form = PersonForm.objects.get(slug=self.kwargs["slug"])
        except PersonForm.DoesNotExist:
            raise Http404("Ce formulaire n'existe pas.")

        if not self.person_form.config.get("public"):
            messages.add_message(
                request,
                messages.ERROR,
                "Les réponses à ce formulaire ne sont pas publiques.",
            )
            return HttpResponseRedirect(
                reverse("view_person_form", args=(self.person_form.pk,))
            )

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return self.person_form.submissions.order_by("created")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(person_form=self.person_form, **kwargs)

        if context["page_obj"]:
            context["submissions"] = get_public_fields(context["page_obj"])
        else:
            context["submissions"] = None

        return context


class PeopleFormSubmissionsPrivateView(DetailView):
    template_name = "people/person_form_private_results.html"
    slug_field = "result_url_uuid"
    slug_url_kwarg = "uuid"
    queryset = PersonForm.objects.all()

    def get_context_data(self, **kwargs):
        submission_qs = self.object.submissions.all()

        headers, submissions = get_formatted_submissions(
            submission_qs, html=True, include_admin_fields=False
        )

        return {
            "person_form": self.object,
            "headers": headers,
            "submissions": submissions,
        }
