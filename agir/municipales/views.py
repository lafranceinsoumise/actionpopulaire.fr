from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView

from agir.events.models import Event
from agir.municipales.models import CommunePage


class CommuneView(DetailView):
    model = CommunePage
    template_name = "commune.html"
    context_object_name = "commune"

    def get_object(self, queryset=None):
        return get_object_or_404(
            self.model,
            code_departement=self.kwargs["code_departement"],
            slug=self.kwargs["slug"],
        )

    def get_context_data(self, **kwargs):
        kwargs["events"] = Event.objects.upcoming().filter(
            coordinates__coveredby=self.object.coordinates
        )

        return super().get_context_data(**kwargs)
