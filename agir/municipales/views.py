from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView, UpdateView
from rest_framework.generics import ListAPIView

from agir.authentication.view_mixins import (
    SoftLoginRequiredMixin,
    PermissionsRequiredMixin,
)
from agir.events.models import Event
from agir.lib.views import IframableMixin
from agir.municipales.forms import CommunePageForm
from agir.municipales.models import CommunePage
from agir.municipales.serializers import CommunePageSerializer


class CommunePageMixin:
    context_object_name = "commune"

    def get_object(self, queryset=None):
        return get_object_or_404(
            self.get_queryset(),
            code_departement=self.kwargs["code_departement"],
            slug=self.kwargs["slug"],
        )


class CommuneView(CommunePageMixin, IframableMixin, DetailView):
    queryset = CommunePage.objects.filter(published=True)

    def get_template_names(self):
        if self.request.GET.get("iframe"):
            return ["municipales/commune_details_iframe.html"]
        return ["municipales/commune_details.html"]

    def get_context_data(self, **kwargs):
        events = (
            Event.objects.upcoming()
            .filter(coordinates__intersects=self.object.coordinates)
            .order_by("start_time")
        )
        paginator = Paginator(events, 5)
        kwargs["events"] = paginator.get_page(self.request.GET.get("events_page"))
        kwargs["change_commune"] = self.request.user.has_perm(
            "municipales.change_communepage", self.object
        )

        return super().get_context_data(**kwargs)


class SearchView(ListAPIView):
    serializer_class = CommunePageSerializer

    def get_queryset(self):
        q = self.request.query_params.get("q")

        if not q:
            return CommunePage.objects.none()

        return CommunePage.objects.filter(published=True).search(q)


class CommuneChangeView(
    CommunePageMixin, SoftLoginRequiredMixin, PermissionsRequiredMixin, UpdateView
):
    queryset = CommunePage.objects.filter(published=True)
    form_class = CommunePageForm
    template_name = "municipales/commune_change.html"
    permissions_required = ("municipales.change_communepage",)

    def get_success_url(self):
        return self.object.get_absolute_url()
