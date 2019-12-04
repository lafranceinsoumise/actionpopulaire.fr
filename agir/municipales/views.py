from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView
from rest_framework.generics import ListAPIView

from agir.events.models import Event
from agir.lib.views import IframableMixin
from agir.municipales.models import CommunePage
from agir.municipales.serializers import CommunePageSerializer


class CommuneView(IframableMixin, DetailView):
    model = CommunePage
    context_object_name = "commune"

    def get_object(self, queryset=None):
        return get_object_or_404(
            self.model,
            code_departement=self.kwargs["code_departement"],
            slug=self.kwargs["slug"],
        )

    def get_template_names(self):
        if self.request.GET.get("iframe"):
            return ["municipales/commune_details_iframe.html"]
        return ["municipales/commune_details.html"]

    def get_context_data(self, **kwargs):
        events = (
            Event.objects.upcoming()
            .filter(coordinates__coveredby=self.object.coordinates)
            .order_by("start_time")
        )
        paginator = Paginator(events, 5)
        kwargs["events"] = paginator.get_page(self.request.GET.get("events_page"))

        return super().get_context_data(**kwargs)


class SearchView(ListAPIView):
    serializer_class = CommunePageSerializer

    def get_queryset(self):
        q = self.request.query_params.get("q")

        if not q:
            return CommunePage.objects.none()

        return CommunePage.objects.search(q)
