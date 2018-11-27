from django.urls import reverse_lazy
from django.views.generic import UpdateView, TemplateView

from agir.authentication.view_mixins import SoftLoginRequiredMixin
from agir.front.view_mixins import SimpleOpengraphMixin
from agir.people.forms import ProfileForm


class ChangeProfileView(SoftLoginRequiredMixin, UpdateView):
    template_name = "people/profile.html"
    form_class = ProfileForm
    success_url = reverse_lazy("confirmation_profile")

    def get_object(self, queryset=None):
        """Get the current user as the view object"""
        return self.request.user.person


class ChangeProfileConfirmationView(SimpleOpengraphMixin, TemplateView):
    template_name = "people/confirmation_profile.html"
