import csv
from uuid import uuid4

from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from agir.people.person_forms.display import get_formatted_submissions
from agir.people.person_forms.models import PersonForm


class FormSubmissionViewsMixin:
    def get_form_submission_qs(self, form):
        return form.submissions.all()

    def generate_result_table(self, form, html=True, fieldsets_titles=True):
        submission_qs = self.get_form_submission_qs(form)

        headers, submissions = get_formatted_submissions(
            submission_qs, html=html, fieldsets_titles=fieldsets_titles
        )

        return {"form": form, "headers": headers, "submissions": submissions}

    def view_results(self, request, pk):
        if not self.has_change_permission(request) or not request.user.has_perm(
            "people.change_personform"
        ):
            raise PermissionDenied

        form = PersonForm.objects.get(id=pk)
        table = self.generate_result_table(form)

        context = {
            "has_change_permission": True,
            "title": _("Réponses du formulaire: %s") % form.title,
            "opts": self.model._meta,
            "form": table["form"],
            "headers": table["headers"],
            "submissions": table["submissions"],
        }

        return TemplateResponse(request, "admin/personforms/view_results.html", context)

    def download_results(self, request, pk):
        if not self.has_change_permission(request):
            raise PermissionDenied()

        form = get_object_or_404(PersonForm, id=pk)
        table = self.generate_result_table(form, html=False, fieldsets_titles=False)

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="{0}.csv"'.format(
            form.slug
        )

        writer = csv.writer(response)
        writer.writerow(table["headers"])
        for submission in table["submissions"]:
            writer.writerow(submission)

        return response

    def create_result_url(self, request, pk, clear=False):
        if not self.has_change_permission(request):
            raise PermissionDenied()

        form = get_object_or_404(PersonForm, id=pk)
        form.result_url_uuid = None if clear else uuid4()
        form.save()

        return HttpResponseRedirect(
            reverse("admin:people_personform_change", args=[pk])
        )
