from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView

from agir.authentication.view_mixins import SoftLoginRequiredMixin
from agir.elus.forms import CreerMandatMunicipalForm, MandatMunicipalForm
from agir.elus.models import MandatMunicipal


class BaseMandatView(SoftLoginRequiredMixin):
    model = MandatMunicipal
    success_url = reverse_lazy("mandats")
    context_object_name = "mandat"

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs, person=self.request.user.person)

    def get_form_kwargs(self):
        return {"person": self.request.user.person, **super().get_form_kwargs()}


class CreerMandatMunicipalView(BaseMandatView, CreateView):
    form_class = CreerMandatMunicipalForm
    template_name = "elus/creer_mandat_municipal.html"


class ModifierMandatMunicipalView(BaseMandatView, UpdateView):
    form_class = MandatMunicipalForm
    template_name = "elus/modifier_mandat_municipal.html"


class SupprimerMandatMunicipalView(BaseMandatView, DeleteView):
    template_name = "elus/supprimer_mandat_municipal.html"
