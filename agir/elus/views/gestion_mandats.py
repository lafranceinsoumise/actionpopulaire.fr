from data_france.models import CollectiviteDepartementale, CollectiviteRegionale
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView

from agir.authentication.view_mixins import SoftLoginRequiredMixin
from agir.elus.forms import (
    MandatMunicipalForm,
    MandatDepartementalForm,
    MandatRegionalForm,
    MandatConsulaireForm,
)
from agir.elus.models import (
    MandatMunicipal,
    MandatDepartemental,
    MandatRegional,
    MandatConsulaire,
)


class BaseMandatView(SoftLoginRequiredMixin):
    success_url = reverse_lazy("mandats")
    context_object_name = "mandat"
    mandat_adjectif = None

    def get_mandat_adjectif(self):
        return self.mandat_adjectif

    def get_conseil_avec_charniere(self):
        return None

    def get_context_data(self, **kwargs):
        if getattr(self, "object"):
            kwargs.setdefault(
                "conseil_avec_charniere",
                self.get_conseil_avec_charniere(),
            )

        return super().get_context_data(
            **kwargs,
            person=self.request.user.person,
            mandat_adjectif=self.get_mandat_adjectif(),
        )

    def get_queryset(self):
        return self.model.objects.filter(person=self.request.user.person)

    def get_form_kwargs(self):
        return {"person": self.request.user.person, **super().get_form_kwargs()}


class BaseMandatMunicipal(BaseMandatView):
    model = MandatMunicipal
    form_class = MandatMunicipalForm
    mandat_adjectif = "municipal⋅e"

    def get_conseil_avec_charniere(self):
        if self.object.conseil:
            return self.object.conseil.nom_avec_charniere
        return "d'une commune inconnue"


class CreerMandatMunicipalView(BaseMandatMunicipal, CreateView):
    template_name = "elus/creer_mandat_conseil.html"


class ModifierMandatMunicipalView(BaseMandatMunicipal, UpdateView):
    template_name = "elus/modifier_mandat_conseil.html"


class SupprimerMandatMunicipalView(BaseMandatMunicipal, DeleteView):
    template_name = "elus/supprimer_mandat_conseil.html"


class BaseMandatDepartemental(BaseMandatView):
    model = MandatDepartemental

    def get_mandat_adjectif(self):
        if getattr(self, "object"):
            if (
                self.object.conseil.type
                == CollectiviteDepartementale.TYPE_CONSEIL_DEPARTEMENTAL
            ):
                return "départemental⋅e"
            return "métropolitain⋅e"
        return "départemental⋅e ou métropolitain⋅e"

    def get_conseil_avec_charniere(self):
        if self.object.conseil:
            return self.object.conseil.nom_avec_charniere
        return "d'un département inconnu"


class CreerMandatDepartementalView(BaseMandatDepartemental, CreateView):
    form_class = MandatDepartementalForm
    template_name = "elus/creer_mandat_conseil.html"


class ModifierMandatDepartementalView(BaseMandatDepartemental, UpdateView):
    form_class = MandatDepartementalForm
    template_name = "elus/modifier_mandat_conseil.html"


class SupprimerMandatDepartementalView(BaseMandatDepartemental, DeleteView):
    template_name = "elus/supprimer_mandat_conseil.html"


class BaseMandatRegional(BaseMandatView):
    model = MandatRegional

    def get_mandat_adjectif(self):
        if getattr(self, "object") and self.object.conseil:
            if self.object.conseil.type == CollectiviteRegionale.TYPE_CONSEIL_REGIONAL:
                return "régional⋅e"
            return "de collectivité unique"
        return "régional⋅e ou de collectivité unique"

    def get_conseil_avec_charniere(self):
        if self.object.conseil:
            return self.object.conseil.nom_avec_charniere
        return "d'une région inconnue"


class CreerMandatRegionalView(BaseMandatRegional, CreateView):
    form_class = MandatRegionalForm
    template_name = "elus/creer_mandat_conseil.html"


class ModifierMandatRegionalView(BaseMandatRegional, UpdateView):
    form_class = MandatRegionalForm
    template_name = "elus/modifier_mandat_conseil.html"


class SupprimerMandatRegionalView(BaseMandatRegional, DeleteView):
    template_name = "elus/supprimer_mandat_conseil.html"


class BaseMandatConsulaire(BaseMandatView):
    model = MandatConsulaire

    def get_mandat_adjectif(self):
        return "consulaire"

    def get_conseil_avec_charniere(self):
        if self.object.conseil:
            return f"({self.object.conseil.nom})"
        return "(circonscription non renseignée)"


class CreerMandatConsulaireView(BaseMandatConsulaire, CreateView):
    form_class = MandatConsulaireForm
    template_name = "elus/creer_mandat_conseil.html"


class ModifierMandatConsulaireView(BaseMandatConsulaire, UpdateView):
    form_class = MandatConsulaireForm
    template_name = "elus/modifier_mandat_conseil.html"


class SupprimerMandatConsulaireView(BaseMandatConsulaire, DeleteView):
    template_name = "elus/supprimer_mandat_conseil.html"
