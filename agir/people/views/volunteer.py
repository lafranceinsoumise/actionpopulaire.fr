from django.urls import reverse_lazy
from django.views.generic import UpdateView, TemplateView

from agir.authentication.view_mixins import SoftLoginRequiredMixin
from agir.people.forms import VolunteerForm


class VolunteerView(SoftLoginRequiredMixin, UpdateView):
    template_name = "people/volunteer.html"
    form_class = VolunteerForm
    success_url = reverse_lazy("confirmation_volunteer")

    def get_object(self, queryset=None):
        """Get the current user as the view object"""
        return self.request.user.person


class VolunteerConfirmationView(TemplateView):
    template_name = "people/confirmation_volunteer.html"
