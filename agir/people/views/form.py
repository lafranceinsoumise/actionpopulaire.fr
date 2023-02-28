import csv
from urllib.parse import urljoin

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.core.files import File
from django.http import Http404
from django.http.response import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.templatetags.static import static
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.html import escape
from django.views.decorators.cache import never_cache
from django.views.generic import UpdateView, DetailView
from django.views.generic.list import ListView

from agir.events.models import Event
from agir.front.view_mixins import ObjectOpengraphMixin
from agir.mailing.actions import create_campaign_from_submission
from agir.people import tasks
from agir.people.models import PersonForm, PersonFormSubmission
from agir.people.person_forms.actions import get_people_form_class
from agir.people.person_forms.display import default_person_form_display


class BasePeopleFormView(UpdateView, ObjectOpengraphMixin):
    queryset = PersonForm.objects.published()
    template_name = "people/person_form.html"

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)
        self.person_form_instance = self.get_person_form_instance()

    def get_meta_title(self):
        if self.person_form_instance.title:
            return "{} — {}".format(self.person_form_instance.title, self.title_suffix)
        return self.title_suffix

    def get_meta_description(self):
        return self.person_form_instance.meta_description

    def get_meta_image(self):
        if self.person_form_instance.meta_image:
            return self.person_form_instance.meta_image.url
        return urljoin(settings.FRONT_DOMAIN, static("front/assets/og_image_NSP.jpg"))

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

    def get_person_form_instance(self):
        try:
            return self.get_queryset().get(slug=self.kwargs["slug"])
        except PersonForm.DoesNotExist:
            raise Http404("Ce formulaire n'existe pas.")

    def get_form_class(self):
        return get_people_form_class(self.person_form_instance)

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            hide_feedback_button=True,
            person_form=self.person_form_instance,
            is_authorized=self.person_form_instance.is_authorized(self.object),
            **kwargs,
        )

    def dispatch(self, request, *args, **kwargs):
        if self.person_form_instance.allow_anonymous or request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)

        return redirect_to_login(request.get_full_path())

    def post(self, request, *args, **kwargs):
        if (
            not self.person_form_instance.is_open
            or not self.person_form_instance.is_authorized(self.get_object())
        ):
            return self.get(request, *args, **kwargs)
        return super().post(request, *args, **kwargs)

    def make_data_url_from_image_file(self, file: File):
        if "image" not in file.content_type:
            return file.name

        prefix = f"data:{file.content_type};base64,"
        fin = file.open("rb")
        contents = fin.read()
        import base64

        data_url = prefix + base64.b64encode(contents).decode("utf-8")
        return data_url

    def form_valid(self, form):
        if (
            self.person_form_instance.campaign_template is not None
            and "preview" in self.request.POST
        ):
            preview = self.person_form_instance.campaign_template.message_content_html
            for field in form.cleaned_data:
                value = form.cleaned_data[field]
                # Generate a data URL image for the email preview
                if isinstance(value, File):
                    value = self.make_data_url_from_image_file(value)
                preview = preview.replace(f"[{field}]", escape(value))

            return HttpResponse(preview)

        r = super().form_valid(form)

        if self.person_form_instance.send_confirmation:
            tasks.send_person_form_confirmation.delay(form.submission.pk)
        if self.person_form_instance.send_answers_to:
            tasks.send_person_form_notification.delay(form.submission.pk)
        if self.person_form_instance.lien_feuille_externe:
            tasks.copier_reponse_vers_feuille_externe.delay(form.submission.pk)

        if self.person_form_instance.campaign_template:
            data = {}
            for key, value in form.submission.data.items():
                data[key] = value
            create_campaign_from_submission(
                data,
                form.submission.person,
                self.person_form_instance.campaign_template,
            )

        return r


@method_decorator(never_cache, name="get")
class PeopleFormNewSubmissionView(BasePeopleFormView):
    def dispatch(self, *args, **kwargs):
        event = Event.objects.filter(
            subscription_form=self.person_form_instance
        ).first()

        if event is not None:
            return redirect("rsvp_event", event.pk)

        if self.person_form_instance.editable and self.request.user.is_authenticated:
            existing_submission = PersonFormSubmission.objects.filter(
                person=self.request.user.person, form=self.person_form_instance
            ).last()
            if existing_submission is not None:
                messages.add_message(
                    self.request,
                    messages.INFO,
                    "Vous avez déjà rempli ce formulaire, mais vous pouvez modifier certaines de vos réponses.",
                )
                return redirect(
                    "edit_person_form_submission",
                    slug=self.person_form_instance.slug,
                    pk=existing_submission.pk,
                )

        return super().dispatch(*args, **kwargs)


@method_decorator(never_cache, name="get")
class PeopleFormEditSubmissionView(BasePeopleFormView):
    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated or self.request.user.person is None:
            return redirect_to_login(request.get_full_path())
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        if not self.person_form_instance.editable:
            raise Http404()

        kwargs = super().get_form_kwargs()
        kwargs["submission"] = get_object_or_404(
            PersonFormSubmission, pk=self.kwargs["pk"]
        )

        if kwargs["submission"].person is None:
            raise PermissionDenied("Ce formulaire ne peut plus être modifié")

        if kwargs["submission"].person != self.request.user.person:
            raise PermissionDenied(
                "Impossible de modifier le formulaire de quelqu'un d'autre"
            )

        return kwargs

    def get_success_url(self):
        event = Event.objects.filter(
            subscription_form=self.person_form_instance
        ).first()

        if event is not None:
            return reverse("rsvp_event", kwargs={"pk": event.pk})

        return super().get_success_url()

    def get(self, request, *args, **kwargs):
        try:
            return super(PeopleFormEditSubmissionView, self).get(
                request, *args, **kwargs
            )
        except PermissionDenied as e:
            messages.add_message(self.request, messages.ERROR, e)
            return HttpResponseRedirect(reverse("dashboard"))


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
            context["submissions"] = default_person_form_display.get_public_fields(
                context["page_obj"]
            )
        else:
            context["submissions"] = None

        return context


class PeopleFormSubmissionsPrivateView(DetailView):
    template_name = "people/person_form_private_results.html"
    slug_field = "result_url_uuid"
    slug_url_kwarg = "uuid"
    queryset = PersonForm.objects.all()

    def get_context_data(self, **kwargs):
        headers, submissions = default_person_form_display.get_formatted_submissions(
            self.object,
            html=False,
            include_admin_fields=self.object.config.get("link_private_fields", False),
        )

        return {
            "person_form": self.object,
            "headers": headers,
            "submissions": submissions,
        }

    def get(self, request, *args, **kwargs):
        if request.GET.get("format") == "csv":
            return self.get_csv(request)
        return super().get(request, *args, **kwargs)

    def get_csv(self, request):
        self.object = form = self.get_object()

        headers, submissions = default_person_form_display.get_formatted_submissions(
            form,
            html=False,
            include_admin_fields=self.object.config.get("link_private_fields", False),
            resolve_labels=bool(request.GET.get("resolve_labels")),
            resolve_values=bool(request.GET.get("resolve_values")),
        )

        response = HttpResponse(content_type="text/csv")
        response[
            "Content-Disposition"
        ] = f'attachment; filename="{self.object.slug}.csv"'

        writer = csv.writer(response)
        writer.writerow(headers)
        writer.writerows(submissions)

        return response
