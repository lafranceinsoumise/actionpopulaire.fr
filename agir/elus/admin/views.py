from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import TemplateView

from agir.elus.models import RechercheParrainageMaire
from agir.lib.admin import AdminViewMixin


class ChangerStatutBaseView(AdminViewMixin, TemplateView):
    statut = None

    def dispatch(self, request, *args, **kwargs):
        self.object = get_object_or_404(
            RechercheParrainageMaire, pk=kwargs["object_id"]
        )

        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object.statut = self.statut
        self.object.save(update_fields=["statut"])

        return HttpResponseRedirect(
            reverse(
                "admin:elus_rechercheparrainagemaire_change", args=(self.object.id,)
            )
        )

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs, object=self.object)


class ConfirmerParrainageView(ChangerStatutBaseView):
    statut = RechercheParrainageMaire.Statut.VALIDEE
    template_name = "elus/admin/confirmer_parrainage.html"


class AnnulerParrainageView(ChangerStatutBaseView):
    statut = RechercheParrainageMaire.Statut.ANNULEE
    template_name = "elus/admin/annuler_parrainage.html"
